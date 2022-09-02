<template>
  <section id="dashboard">
    <mdb-card class="mb-4">
      <mdb-card-body class="d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Run selected implementations on benchmarks
        </h4>
      </mdb-card-body>
    </mdb-card>
    <section>
      <mdb-row v-show="! isCustomRunRunning">
        <mdb-col xl="4" md="6" class="mb-r" v-for="(algorithm, index) in algorithms" :key="algorithm.name">
          <mdb-card class="cascading-admin-card">
            <div class="admin-up">
              <mdb-view>
              <mdb-card-title>
                  <div>
                    <mdb-icon :icon="algorithm.symbol" fas class="m-2 primary-color" size="3x"/>
                    <strong class="algorithmName">{{algorithm.name}}</strong>
                  </div>
              </mdb-card-title>
              </mdb-view>
              <div class="taskNumber">
                <p>{{algorithm.task}}</p>
              </div>
            </div>
            <mdb-card-body>
              <mdb-container>
                <p class="benchmarkSelector">SELECT BENCHMARK:</p>
                <select class="browser-default custom-select benchmarkPossibilities" multiple v-model="selected[index]">
                  <option v-for="value in benchmarks" :key="value">
                    {{value}}
                  </option>
                </select>
                <mdb-row class="logSelector">
                  SELECT LOG LEVEL:
                </mdb-row>
                <mdb-row class="justify-content-center">
                  <div class="custom-control custom-radio custom-control-inline">
                    <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelDebug`" value="DEBUG" v-model="selectedLogLevels[index]">
                    <label class="custom-control-label" :for="`${index}__LogLevelDebug`">DEBUG</label>
                  </div>
                  <div class="custom-control custom-radio custom-control-inline">
                    <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelInfo`" value="INFO" v-model="selectedLogLevels[index]">
                    <label class="custom-control-label" :for="`${index}__LogLevelInfo`">INFO</label>
                  </div>
                  <div class="custom-control custom-radio custom-control-inline">
                    <input type="radio" :name="`radioLogLevel__${index}`" class="custom-control-input" :id="`${index}__LogLevelWarning`" value="WARNING" v-model="selectedLogLevels[index]">
                    <label class="custom-control-label" :for="`${index}__LogLevelWarning`">WARNING</label>
                  </div>
                </mdb-row>
                <mdb-row class="justify-content-center">
                  <mdb-btn :color="runButtonColor(index)" class="runButton" @click="runBenchmarkClicked(algorithm.name,selected[index][0], index)" :disabled="runButtonIsDisabled(index)">{{runButtonText(index)}}</mdb-btn>
                  <mdb-btn :color="runButtonColor(index)" class="runButton" @click="runAllClicked(algorithm.name, index)" v-if="! runButtonDisplaysStopMessage(index)" :disabled="runButtonIsDisabled(index)">RUN ALL</mdb-btn>
                </mdb-row>
                <mdb-row v-if="displayedModalButtons[index]" class="justify-content-center">
                  <mdb-btn color="primary" class="runButton" @click="clickDisplayModalButton(index)" >Display results</mdb-btn>
                </mdb-row>
                <section v-if="shouldProgressBeDisplayed(index)">
                  <mdb-row class="logSelector" >
                    RUNNING: {{runningBenchmark}}
                  </mdb-row>
                  <mdb-row class="progress">
                    <div aria-valuemax="100" aria-valuemin="0" :aria-valuenow="progressBarValue" class="progress-bar bg-primary" role="progressbar"
                      :style="progressBarStyle"></div>
                  </mdb-row>
                </section>
                <mdb-modal size="lg" :show="displayedModals[index]" @close="closeModal(index)" scrollable>
                  <mdb-modal-header>
                    <mdb-modal-title>Algorithm result</mdb-modal-title>
                  </mdb-modal-header>
                  <mdb-modal-body v-html="modalMessages[index]">
                  </mdb-modal-body>
                  <mdb-modal-footer>
                    <mdb-btn color="secondary" @click.native="closeModal(index)">Close</mdb-btn>
                  </mdb-modal-footer>
                </mdb-modal>
              </mdb-container>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-row v-show="isCustomRunRunning">
        <mdb-card-body>
          <mdb-row class="justify-content-center margin-top-little">Unfortunately <strong>no benchmark can be ran right now</strong> as there is another custom run running</mdb-row>
          <mdb-row class="justify-content-center margin-top-little">We are checking the availability of Benchmark on the background</mdb-row>
        </mdb-card-body>
      </mdb-row>
    </section>
  </section>
</template>

<script src="@/assets/js/benchmarks.js" />
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped src="@/assets/styles/benchmarks.css" />
