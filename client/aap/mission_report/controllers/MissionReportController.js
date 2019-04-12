import {DATE_FILTERS} from 'superdesk-analytics/client/search/directives/DateFilters.js';

MissionReportController.$inject = [
    '$scope',
    'savedReports',
    'notify',
    'lodash',
    'searchReport',
    '$q',
    'missionReportChart',
];

/**
 * @ngdoc controller
 * @module superdesk.aap.mission_report
 * @name MissionReportController
 * @requires $scope
 * @requires savedReports
 * @requires notify
 * @requires lodash
 * @requires searchReport
 * @requires $q
 * @requires missionReportChart
 * @description Controller for the Mission Analytics report
 */
export function MissionReportController(
    $scope,
    savedReports,
    notify,
    _,
    searchReport,
    $q,
    missionReportChart
) {
    /**
     * @ngdoc method
     * @name MissionReportController#init
     * @description Initializes the scope parameters for use with the form and charts
     */
    this.init = () => {
        $scope.ready = false;
        $scope.dateFilters = [
            DATE_FILTERS.YESTERDAY,
            DATE_FILTERS.RELATIVE,
        ];

        this.initDefaultParams();

        savedReports.selectReportFromURL();

        $scope.ready = true;
    };

    /**
     * @ngdoc method
     * @name MissionReportController#initDefaultParams
     * @description Sets the default report parameters
     */
    this.initDefaultParams = () => {
        $scope.currentParams = {
            params: {
                dates: {
                    filter: 'yesterday',
                },
                size: 2000,
                repos: {published: true},
                must_not: {
                    categories: [],
                    genre: [],
                    ingest_providers: [],
                    stages: [],
                },
                reports: {
                    summary: true,
                    categories: true,
                    corrections: true,
                    kills: true,
                    takedowns: true,
                    updates: true,
                    sms_alerts: true,
                },
            },
            report: 'mission_report',
        };

        $scope.defaultReportParams = _.cloneDeep($scope.currentParams);
    };

    $scope.isDirty = () => true;

    $scope.$watch(() => savedReports.currentReport, (newReport) => {
        if (_.get(newReport, '_id')) {
            $scope.currentParams = _.cloneDeep(savedReports.currentReport);
        } else {
            $scope.currentParams = _.cloneDeep($scope.defaultReportParams);
        }
    }, true);

    /**
     * @ngdoc method
     * @name MissionReportController#generate
     * @description Using the current form parameters, query the Search API and update the chart configs
     */
    $scope.generate = () => {
        $scope.beforeGenerateChart();
        $scope.changeContentView('report');

        const params = _.cloneDeep($scope.currentParams.params);

        $scope.runQuery(params).then((data) => {
            missionReportChart.createChart(data, params)
                .then((config) => {
                    $scope.changeReportParams(config)
                });
        }).catch((error) => {
            notify.error(error);
        });
    };

    $scope.getReportParams = () => (
        $q.when(_.cloneDeep($scope.currentParams))
    );

    this.init();
}
