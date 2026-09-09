"""Exercise the pinned server's original parameter filter, without its services.

Usage: python3 off-search-filter-reproduction.py /path/to/flattened-source-files
The original filter executes in Perl; request retrieval and downstream query
construction are spies. This does not run a server or return product results.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


HASHES = {
    "lib__ProductOpener__Display.pm": "0b736cf7ca56bd1f5465d45be2a0f57acd78906d6bd8d58c3176de5aefd8b5a3",
    "lib__ProductOpener__Routing.pm": "640484535b09fe0b8a1be84408683d835168f09674bf79f24cd4ec8462e484f9",
    "cgi__display.pl": "3819e79dbf7d9e657cb89e17805694f62d79893b07cfcc6619bcffc4f630e99c",
}


def main():
    source_dir = Path(sys.argv[1])
    for filename, expected in HASHES.items():
        actual = hashlib.sha256((source_dir / filename).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Unexpected source revision: {filename}")

    source = (source_dir / "lib__ProductOpener__Display.pm").read_text()
    start = source.index("my %ignore_params = (")
    end = source.index("\n=head2 add_params_to_query", start)
    original = source[start:end]
    cases = [
        {"name": "ordinary text", "params": {"search_terms": "mineral water"}},
        {"name": "distinct nonce", "params": {"search_terms": "humanifest-nonmatching-93f6"}},
        {"name": "no text", "params": {}},
        {"name": "structured control", "params": {"search_terms": "mineral water", "brands_tags": "en:test-brand"}},
    ]
    for case in cases:
        case["params"].update(page="2", page_size="10", sort_by="unique_scans")

    harness = r'''
use strict;
use warnings;
use feature 'signatures';
no warnings 'experimental::signatures';
use JSON::PP;
my ($current_params, $forwarded, $owner_calls);
sub get_all_request_params ($request) { return { %$current_params }; }
sub add_params_to_query ($params, $query) { $forwarded = { %$params }; }
sub add_country_and_owner_filters_to_query ($request, $query) { $owner_calls++; }
'''
    harness += original
    harness += r'''
my $cases = decode_json(do { local $/; <STDIN> });
my @results;
for my $case (@$cases) {
    $current_params = $case->{params};
    $forwarded = undef;
    $owner_calls = 0;
    my $request = {};
    add_params_and_filters_to_query($request, {});
    push @results, { name => $case->{name}, forwarded_filters => $forwarded,
                    request => $request, owner_filter_calls => $owner_calls };
}
print encode_json(\@results);
'''
    with tempfile.TemporaryDirectory(prefix="humanifest-off-filter-") as temp:
        script = Path(temp) / "filter.pl"
        script.write_text(harness)
        result = subprocess.run(
            ["/usr/bin/perl", str(script)], input=json.dumps(cases),
            text=True, capture_output=True, check=True, timeout=10,
            env={"PATH": "/usr/bin:/bin", "TZ": "UTC"},
        )
    results = json.loads(result.stdout)
    assert [r["forwarded_filters"] for r in results] == [
        {}, {}, {}, {"brands_tags": "en:test-brand"},
    ]
    for result in results:
        assert result["request"] == {"page": 2, "page_size": 10, "sort_by": "unique_scans"}
        assert result["owner_filter_calls"] == 1
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
