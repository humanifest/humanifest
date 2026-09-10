/* global angular, chai, describe, it, beforeEach, afterEach, module, inject, Q, sinon */
// Synthetic current-behavior probes against the original controller in Chrome.
// Uses Q in the same way as CHT's existing controller tests. These assertions
// reproduce the fault; they must not become acceptance assertions for a fix.
describe('Humanifest edit-user load reproduction', () => {
  let scope;
  let create;
  let settings;
  let http;
  let log;

  beforeEach(() => {
    module('controllers');
    inject(($controller, $rootScope) => {
      scope = $rootScope.$new();
      scope.model = {
        _id: 'synthetic-user', name: 'synthetic-user', oidc_login: true,
        fullname: 'Synthetic User', roles: ['field-worker'], facility_id: [],
      };
      scope.setError = sinon.stub();
      settings = sinon.stub().resolves({ roles: { 'field-worker': { offline: true } } });
      http = { get: sinon.stub().resolves({ data: { oidc_username: 'synthetic-oidc' } }) };
      log = { error: sinon.stub() };
      create = () => $controller('EditUserCtrl', {
        $scope: scope, $rootScope, $q: Q, $http: http, $log: log,
        $translate: sinon.stub(),
        // No modal is rendered in these controller probes; prevent unrelated
        // contact-widget work. Existing target tests cover that normal path.
        $uibModalInstance: { rendered: new Promise(() => {}), dismiss: sinon.stub() },
        ContactTypes: {}, CreateUser: {}, DB: sinon.stub(), Select2Search: sinon.stub(),
        Settings: settings, Translate: {}, UpdateUser: sinon.stub(),
        DataContext: Promise.resolve({
          getDatasource: () => ({ v1: { hasPermissions: () => false } }),
        }),
      });
    });
  });

  afterEach(() => scope.$destroy());

  it('populates the edit model when the same synthetic SSO request succeeds', async () => {
    await create().setupPromise;
    chai.expect(scope.editUserModel.username).to.equal('synthetic-user');
    chai.expect(scope.editUserModel.oidc_username).to.equal('synthetic-oidc');
    chai.expect(log.error.called).to.equal(false);
    chai.expect(http.get.calledOnceWithExactly('/api/v2/users/synthetic-user')).to.equal(true);
  });

  it('logs a rejected SSO request but leaves no edit model or modal error', async () => {
    const failure = new Error('Synthetic offline SSO request');
    http.get.rejects(failure);
    await create().setupPromise;
    chai.expect(log.error.calledOnceWithExactly('Error determining user model', failure)).to.equal(true);
    chai.expect(scope.editUserModel).to.equal(undefined);
    chai.expect(scope.setError.called).to.equal(false);
  });

  it('also leaves the model unset when settings fail for a non-SSO user', async () => {
    scope.model.oidc_login = false;
    const failure = new Error('Synthetic settings failure');
    settings.rejects(failure);
    await create().setupPromise;
    chai.expect(http.get.called).to.equal(false);
    chai.expect(log.error.calledOnceWithExactly('Error determining user model', failure)).to.equal(true);
    chai.expect(scope.editUserModel).to.equal(undefined);
    chai.expect(scope.setError.called).to.equal(false);
  });
});
