<template>
  <section id="custom-run">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Run selected implementations on custom inputs.
        </h4>
      </mdb-card-body>
    </mdb-card>
    <section>
      <mdb-row>
        <mdb-col class="mb-r">
          <mdb-card class="cascading-admin-card" v-show="! isBenchmarkRunning">
            <div class="admin-up">
              <mdb-view>
              <mdb-card-title>
                <div>
                  <mdb-icon icon="microchip" fas class="m-2 primary-color" size="3x"/>
                  <section class="top-card-section">
                    <mdb-row class="benchmarkSelector justify-content-center">{{defaultAlgorithmName}}</mdb-row>
                    <mdb-row class="justify-content-center">
                      <strong>
                        <select
                          class="browser-default custom-select algo-select"
                          v-model="selectedAlgorithmName"
                        >
                          <option selected disabled>{{defaultAlgorithmName}}</option>
                          <option v-for="(algo, index) in algorithms" :key="index">
                            {{algo.name}}
                          </option>
                          </select>
                      </strong>
                    </mdb-row>
                    <mdb-row class="taskNumber justify-content-end">
                      {{selectedAlgorithm.taskName}}
                    </mdb-row>
                  </section>
                </div>
              </mdb-card-title>
              </mdb-view>
            </div>
            <mdb-card-body class="no-up-padding-card-body">
              <mdb-container>
                  <mdb-row class="benchmarkSelector">{{defaultBenchmarkName}}</mdb-row>
                  <mdb-row>
                    <select
                      class="browser-default custom-select benchmarkPossibilities"
                      v-model="selectedBenchmarkName"
                      @change="selectedBenchmarkInputName=defaultBenchmarkInputName"
                    >
                      <option selected disabled>{{defaultBenchmarkName}}</option>
                      <option v-for="(bench, index) in benchmarks" :key="index">
                        {{bench.name}}
                      </option>
                    </select>
                  </mdb-row>
                  <mdb-row v-show="showBenchmarkInputs" class="benchmarkSelector">{{defaultBenchmarkInputName}}</mdb-row>
                  <mdb-row v-show="showBenchmarkInputs">
                    <select
                      class="browser-default custom-select benchmarkPossibilities"
                      v-model="selectedBenchmarkInputName"
                    >
                      <option selected disabled>{{defaultBenchmarkInputName}}</option>
                      <option v-for="(benchIn, index) in selectedBenchmark.inputs" :key="index">
                        {{benchIn}}
                      </option>
                    </select>
                  </mdb-row>
                  <mdb-row v-show="showCustomInputForm">Custom input isn't implemented yet!</mdb-row>
                  <mdb-row v-show="showRunButton" class="justify-content-center margin-top-little">
                    <div class="custom-control custom-radio custom-control-inline">
                      <input type="radio" :name="`radioLogLevel`" class="custom-control-input" :id="`LogLevelDebug`" value="DEBUG" v-model="selectedLogLevel">
                      <label class="custom-control-label" :for="`LogLevelDebug`">DEBUG</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                      <input type="radio" :name="`radioLogLevel`" class="custom-control-input" :id="`LogLevelInfo`" value="INFO" v-model="selectedLogLevel">
                      <label class="custom-control-label" :for="`LogLevelInfo`">INFO</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                      <input type="radio" :name="`radioLogLevel`" class="custom-control-input" :id="`LogLevelWarning`" value="WARNING" v-model="selectedLogLevel">
                      <label class="custom-control-label" :for="`LogLevelWarning`">WARNING</label>
                    </div>
                  </mdb-row>
                  <mdb-row v-show="showBenchmarkInputButton" class="justify-content-center">
                    <mdb-btn v-show="showRunButton" :class="runButtonClass" @click="runButtonClicked(selectedAlgorithmName, selectedBenchmarkName, selectedBenchmarkInputName, selectedLogLevel)">{{runButtonText}}</mdb-btn>
                    <mdb-btn class="run-button-start" @click="showInputClicked(selectedBenchmarkName, selectedBenchmarkInputName)">Show Benchmark Input</mdb-btn>
                  </mdb-row>
              </mdb-container>
            </mdb-card-body>
          </mdb-card>
          <mdb-card v-show="isBenchmarkRunning">
            <mdb-card-body>
              <mdb-row class="justify-content-center margin-top-little">Unfortunately <strong>no input can be ran right now</strong> as there is another benchmark running</mdb-row>
              <mdb-row class="justify-content-center margin-top-little">We are checking the availability of Custom Run on the background</mdb-row>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-row v-show="showRunResults" class="row-with-logs">
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <mdb-card class="card-with-logs rounded-border custom-margin-top ">
            <mdb-card-title class="blue darken-2 rounded-border text-center card-header-hoverable">
              <h4 class="h4-responsive text-white spaced-title"
                  @click="switchOnModalStd()">Standard Logs from Algorithm</h4>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="stdLogs">
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <mdb-card class="card-with-logs rounded-border custom-margin-top ">
            <mdb-card-title
              class="blue darken-2 rounded-border text-center">
              <li class="list-inline-item card-header-hoverable"
                @click="switchOnModalRedisStd()">
                <h4 class="h4-responsive text-white spaced-title">Standard Redis Worker Logs</h4>
              </li>
              <li class="header-button-style list-inline-item"
                @click="removeStdRedisLogs()">
                <h4 class="h4-responsive text-white">Clear</h4>
              </li>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="redisStdLogs">
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <mdb-card class="card-with-logs rounded-border custom-margin-top ">
            <mdb-card-title class="blue darken-2 rounded-border text-center">
              <li class="list-inline-item card-header-hoverable"
                @click="switchOnModalRedisError()">
                <h4 class="h4-responsive text-white spaced-title">Error Redis Worker Logs</h4>
              </li>
              <li class="header-button-style list-inline-item"
                @click="removeErrorRedisLogs()">
                <h4 class="h4-responsive text-white">Clear</h4>
              </li>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="redisErrorLogs">
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-row v-show="showBenchmarkInputContent">
        <mdb-col col="12">
          <mdb-card>
            <mdb-card-title class="blue darken-2 rounded-border text-center">
                <h4 class="h4-responsive text-white spaced-title">Benchmark Input Content</h4>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="benchmarkInputContent">
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-modal size="fluid" :show="displayModal" @close="displayModal = false" scrollable>
        <mdb-modal-header>
          <mdb-modal-title>{{modalTitle}}</mdb-modal-title>
        </mdb-modal-header>
        <mdb-modal-body v-html="modalMessage">
        </mdb-modal-body>
        <mdb-modal-footer>
          <mdb-btn color="secondary" @click.native="displayModal = false">Close</mdb-btn>
        </mdb-modal-footer>
      </mdb-modal>
    </section>
  </section>
</template>

<script src="@/assets/js/customRun.js" />
<style scoped src="@/assets/styles/customRun.css" />
