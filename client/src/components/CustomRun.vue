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
                      <option v-for="(bench, bench_index) in benchmarks" :key="bench_index">
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
                      <option v-for="(benchIn, entry_index) in selectedBenchmark.inputs" :key="entry_index">
                        {{benchIn}}
                      </option>
                    </select>
                  </mdb-row>
                  <mdb-row v-show="showCustomInputForm">Custom input isn't implemented yet!</mdb-row>
                  <section v-if="selectedAlgorithm.options.length > 0" style="margin-top: 10px; margin-bottom: 10px">
                    <mdb-row class="logSelector">
                      PARAMETERS:
                    </mdb-row>
                    <section
                      v-for="(option, option_index) in selectedAlgorithm.options"
                      :key="option_index"
                    >
                      <mdb-row class="parameterSelector justify-content-between">
                        <div>
                        <a>{{option.name}}:</a>
                        <div class="hintClass">{{option.hint}}</div>
                        </div>
                        <div v-if="option.type=='value'"
                        class="align-self-center">
                          <input v-model="option.default" class="benchmarkPossibilities special-width"/>
                        </div>
                        <div v-if="option.type=='checkbox'"
                        class="align-self-center">
                          <input type="checkbox"
                          :id="`${option_index}_checkbox`"
                          v-model="option.default" />
                        </div>
                        <div v-if="option.type==='list'"
                        class="align-self-center">
                          <select class="browser-default custom-select benchmarkPossibilities special-width" v-model="option.default">
                            <option v-for="value in option.options" :key="value">
                              {{value}}
                            </option>
                          </select>
                        </div>
                      </mdb-row>
                    </section>
                </section>
                <log-selector v-show="showRunButton" :selectedLogLevels="selectedLogLevels" />
                <mdb-row v-show="showBenchmarkInputButton" class="justify-content-center">
                  <mdb-btn v-show="showRunButton" :class="runButtonClass" @click="runButtonClicked(selectedAlgorithm, selectedBenchmarkName, selectedBenchmarkInputName, selectedLogLevels[0])">{{runButtonText}}</mdb-btn>
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
          <modal-card
            :message="stdLogs"
            title="Standard Logs from Algorithm"
            :clearPossibility="false"
          />
        </mdb-col>
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <modal-card
            :message="redisStdLogs"
            title="Standard Redis Worker Logs"
            :clearPossibility="true"
            :clearFunction="removeStdRedisLogsBinded"
          />
        </mdb-col>
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <modal-card
            :message="redisErrorLogs"
            title="Error Redis Worker Logs"
            :clearPossibility="true"
            :clearFunction="removeErrorRedisLogsBinded"
          />
        </mdb-col>
      </mdb-row>
      <mdb-row v-show="showBenchmarkInputContent">
        <mdb-col col="12">
          <modal-card
            :message="benchmarkInputContent"
            title="Benchmark Input Content"
            :clearPossibility="false"
          />
        </mdb-col>
      </mdb-row>
    </section>
  </section>
</template>

<script src="@/assets/js/customRun.js" />
<style scoped src="@/assets/styles/customRun.css" />
