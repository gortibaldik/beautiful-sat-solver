<template>
  <section id="dashboard">
    <mdb-card class="mb-4">
      <mdb-card-body class="d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Run selected implementations on benchmarks
        </h4>
      </mdb-card-body>
    </mdb-card>
    <section class="mt-lg-5">
      <mdb-row>
        <mdb-col xl="4" md="6" class="mb-r" v-for="(algorithm, index) in algorithms" :key="algorithm.name">
          <mdb-card class="cascading-admin-card">
            <div class="admin-up">
              <mdb-view>
              <mdb-card-title>
                  <div>
                    <mdb-icon :icon="symbolsForAlgorithms[index]" fas class="m-2 primary-color" size="3x"/>
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
                <div class="text-center">
                  <mdb-btn color="primary" class="runButton" @click="runBenchmarkClicked(algorithm.name,selected[index][0], index)" :disabled="isDisabled">Run</mdb-btn>
                </div>
                <div class="text-center" :style="displayModalButton(index)">
                  <mdb-btn color="primary" class="runButton" @click="clickDisplayModalButton(index)" >Display results</mdb-btn>
                </div>
                <div class="progress" :style="displayProgressBar(index)">
                  <div aria-valuemax="100" aria-valuemin="0" :aria-valuenow="progressBarValue" class="progress-bar bg-primary" role="progressbar"
                    :style="progressBarStyle"></div>
                </div>
                <mdb-modal :show="displayedModals[index]" @close="closeModal(index)" scrollable>
                  <mdb-modal-header>
                    <mdb-modal-title>Algorithm result</mdb-modal-title>
                  </mdb-modal-header>
                  <mdb-modal-body>
                    {{modalMessages[index]}}
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
    </section>
  </section>
</template>

<script src="@/assets/js/benchmarks.js" />
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped src="@/assets/styles/benchmarks.css" />
