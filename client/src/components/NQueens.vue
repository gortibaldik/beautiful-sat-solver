<template>
  <section id="nqueens">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          N-Queens problem
        </h4>
      </mdb-card-body>
    </mdb-card>
    <section>
      <mdb-row>
        <mdb-col class="mb-r">
          <mdb-card class="cascading-admin-card" v-show="! isOtherTabRunning">
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
                  <section v-if="problem_parameters && problem_parameters.length > 0" style="margin-top: 10px; margin-bottom: 10px">
                    <mdb-row class="logSelector">
                      PROBLEM PARAMETERS:
                    </mdb-row>
                    <section
                      v-for="(parameter, param_index) in problem_parameters"
                      :key="param_index"
                    >
                      <mdb-row class="parameterSelector justify-content-between">
                        <div>
                        <a>{{parameter.name}}:</a>
                        <div class="hintClass">{{parameter.hint}}</div>
                        </div>
                        <div v-if="parameter.type=='value'"
                        class="align-self-center">
                          <input v-model="parameter.default" class="benchmarkPossibilities special-width"/>
                        </div>
                        <div v-if="parameter.type=='checkbox'"
                        class="align-self-center">
                          <input type="checkbox"
                          :id="`${param_index}_p_checkbox`"
                          v-model="parameter.default" />
                        </div>
                        <div v-if="parameter.type==='list'"
                        class="align-self-center">
                          <select class="browser-default custom-select benchmarkPossibilities special-width" v-model="option.default">
                            <option v-for="(value, index) in parameter.options" :key="index">
                              {{value}}
                            </option>
                          </select>
                        </div>
                      </mdb-row>
                    </section>
                  </section>
                  <section v-if="selectedAlgorithm.options.length > 0" style="margin-top: 10px; margin-bottom: 10px">
                    <hr>
                    <mdb-row class="logSelector">
                      ALGORITHM PARAMETERS:
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
                  <mdb-row v-show="showRunButton" class="logSelector">
                    SELECT LOG LEVEL:
                  </mdb-row>
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
                  <mdb-row v-show="showRunButton" class="justify-content-center">
                    <mdb-btn v-show="showRunButton" :class="runButtonClass" @click="runButtonClicked(selectedAlgorithm, selectedLogLevel)">{{runButtonText}}</mdb-btn>
                  </mdb-row>
              </mdb-container>
            </mdb-card-body>
          </mdb-card>
          <mdb-card v-show="isOtherTabRunning">
            <mdb-card-body>
              <mdb-row class="justify-content-center margin-top-little">Unfortunately <strong>no input can be ran right now</strong> as there is another benchmark running</mdb-row>
              <mdb-row class="justify-content-center margin-top-little">We are checking the availability of N-Queens on the background</mdb-row>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
      <mdb-row v-show="showRunResults" class="row-with-logs">
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <mdb-card class="card-with-logs rounded-border custom-margin-top ">
            <mdb-card-title class="blue darken-2 rounded-border text-center card-header-hoverable">
              <h4 class="h4-responsive text-white spaced-title">Standard Logs from Algorithm</h4>
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
            <mdb-card-title class="blue darken-2 rounded-border text-center card-header-hoverable">
              <h4 class="h4-responsive text-white spaced-title">Dimacs SAT Encoding of the problem</h4>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="dimacs_str">
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
        <mdb-col xl="6" md="12" class="mb-r col-with-logs">
          <mdb-card class="card-with-logs rounded-border custom-margin-top ">
            <mdb-card-title class="blue darken-2 rounded-border text-center card-header-hoverable">
              <h4 class="h4-responsive text-white spaced-title">Dimacs SAT Encoding of the problem</h4>
            </mdb-card-title>
            <mdb-card-body>
              <div class="scrollbar-class">
                <mdb-scrollbar v-html="chessBoard" >
                </mdb-scrollbar>
              </div>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
    </section>
  </section>
</template>

<script src="@/assets/js/nqueens.js" />
<style scoped src="@/assets/styles/nqueens.css" />
