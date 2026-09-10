/* global angular, chai, describe, it, before, beforeEach, afterEach, module, inject, Q, sinon */
// Compile the original controller/template/modal directive in a real browser.
// No CHT server, user data, production styling or Bootstrap window is involved.
describe('Humanifest edit-user DOM reproduction', () => {
  let rootScope;
  let scope;
  let element;
  let create;
  let lookup;
  let log;

  // main.js bootstraps document on jQuery ready. Let that finish on the empty
  // page before attaching test DOM, otherwise a second injector recompiles it.
  before(() => new Promise(resolve => {
    angular.element(document).ready(() => setTimeout(resolve, 0));
  }));

  beforeEach(() => {
    module('adminApp');
    module(($provide, $translateProvider) => {
      $provide.value('Auth', { has: () => Promise.resolve(true) });
      $provide.value('TranslationLoader', () => Promise.resolve({}));
      $provide.value('DB', () => { throw new Error('Unexpected database access in synthetic DOM probe'); });
      $provide.value('Session', { userCtx: () => ({ name: 'synthetic-admin' }) });
      $translateProvider.translations('en', { 'Add User': 'Add User', 'Edit User': 'Edit User' });
      $translateProvider.use('en');
    });
    let options;
    const instance = {
      rendered: new Promise(() => {}), closed: new Promise(() => {}),
      result: new Promise(() => {}), dismiss: sinon.stub(),
    };
    module($provide => {
      $provide.value('$uibModal', { open: value => { options = value; return instance; } });
    });
    inject(($rootScope, $controller, $compile, $templateCache, Modal) => {
      rootScope = $rootScope;
      lookup = Q.defer();
      log = { error: sinon.stub() };
      create = () => {
        Modal({
          templateUrl: 'templates/edit_user.html', controller: 'EditUserCtrl',
          model: { _id: 'synthetic-user', name: 'synthetic-user', oidc_login: true,
            fullname: 'Synthetic User', roles: [], facility_id: [] },
        });
        scope = options.scope;
        const controller = $controller(options.controller, {
          $scope: scope, $rootScope, $q: Q, $http: { get: () => lookup.promise }, $log: log,
          $translate: sinon.stub(), $uibModalInstance: instance,
          ContactTypes: {}, CreateUser: {}, DB: sinon.stub(), Select2Search: sinon.stub(),
          Settings: () => Promise.resolve({ roles: {} }), Translate: {}, UpdateUser: sinon.stub(),
          DataContext: Promise.resolve({ getDatasource: () => ({ v1: { hasPermissions: () => false } }) }),
        });
        element = $compile($templateCache.get(options.templateUrl))(scope);
        document.body.appendChild(element[0]);
        rootScope.$digest();
        return controller;
      };
    });
  });

  afterEach(() => {
    if (element) element.remove();
    if (scope) scope.$destroy();
  });

  const input = () => element[0].querySelector('#edit-username');
  const title = () => element[0].querySelector('.modal-header h2').textContent.trim();
  const submit = () => element[0].querySelector('[test-id="modal-submit-btn"]');
  const settle = async () => {
    await new Promise(resolve => setTimeout(resolve, 20));
    rootScope.$digest();
  };
  const expectUnloadedForm = () => {
    chai.expect(input().isConnected).to.equal(true);
    chai.expect(input().getBoundingClientRect().height).to.be.greaterThan(0);
    chai.expect(input().value).to.equal('');
    chai.expect(input().disabled).to.equal(false);
    chai.expect(title()).to.equal('Add User');
    chai.expect(submit().classList.contains('disabled')).to.equal(false);
    chai.expect(submit().getBoundingClientRect().height).to.be.greaterThan(0);
    chai.expect(element[0].querySelector('.modal-footer .alert')).to.equal(null);
  };

  it('shows an editable blank Add User form while an existing-user lookup is pending', async () => {
    const controller = create();
    await settle();
    expectUnloadedForm();
    lookup.resolve({ data: { oidc_username: 'synthetic-oidc' } });
    await controller.setupPromise;
    await settle();
    chai.expect(input().value).to.equal('synthetic-user');
    chai.expect(input().disabled).to.equal(true);
    chai.expect(title()).to.equal('Edit User');
  });

  it('keeps the blank Add User form and no alert after the existing-user lookup fails', async () => {
    const controller = create();
    lookup.reject(new Error('Synthetic offline lookup'));
    await controller.setupPromise;
    await settle();
    expectUnloadedForm();
    chai.expect(log.error.calledOnce).to.equal(true);
    chai.expect(scope.status.error).to.equal(false);
  });
});
