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
            <algorithm-selector 
              :defaultName="defaultAlgorithmName"
              :selectedNameData="selectedAlgorithmName"
              :optionArray="algorithms"
            />
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
                <run-parameters
                  :optionArray="selectedAlgorithm.options"
                  title="PARAMETERS"
                />
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
