module.exports = (shipit) => {
  require('shipit-deploy')(shipit);

  const PROJECT_ROOT_FOLDER = '/home/ubuntu/ML-Infra/';
  const CURRENT_RELEASE_FOLDER = PROJECT_ROOT_FOLDER + 'current';

  shipit.initConfig({
    default: {
      repositoryUrl: 'git@github.com:emilemathieu/ML-Infra.git',
      workspace: '/tmp/ml-infra-deploy',
      deployTo: PROJECT_ROOT_FOLDER,
      branch: 'master',
      keepReleases: 2,
      deleteOnRollback: false,
      shallowClone: false,
    },
    production: {
      shallowClone: false,
      servers: ['ubuntu@34.250.87.12'],
    },
  });

  shipit.task('launchpm2', () => {
    shipit.remote('pm2 startOrRestart '
    + CURRENT_RELEASE_FOLDER
    + '/devops/deployment/' + shipit.environment + '.json');
  });

  shipit.on('deploy', () => {
  });
};