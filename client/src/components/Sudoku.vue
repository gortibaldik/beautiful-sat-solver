<template>
  <section id="nqueens">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Sudoku
        </h4>
      </mdb-card-body>
    </mdb-card>
    <section>
      <mdb-row>
        <mdb-col class="mb-r">
          <mdb-card class="cascading-admin-card" v-show="! isOtherTabRunning">
            <algorithm-selector 
              :defaultName="defaultAlgorithmName"
              :selectedNameData="selectedAlgorithmName"
              :optionArray="algorithms"
            />
            <mdb-card-body class="no-up-padding-card-body">
              <mdb-container>
                <run-parameters
                :optionArray="problem_parameters"
                title="PROBLEM PARAMETERS:"
                />
                <run-parameters
                  :optionArray="selectedAlgorithm.options"
                  title="ALGORITHM PARAMETERS:"
                />
                <log-selector v-show="showRunButton" :selectedLogLevels="selectedLogLevels" />
                <mdb-row class="justify-content-center">
                  <mdb-btn v-show="showRunButton && showSudoku" :class="runButtonClass" @click="runButtonClicked(selectedAlgorithm, selectedLogLevels[0])">{{runButtonText}}</mdb-btn>
                  <mdb-btn :class="runButtonClass" @click="generateSudokuClicked()" :disabled="! generateAgain">Generate Sudoku</mdb-btn>
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
      <mdb-row class="row-with-logs">
        <mdb-col v-show="showRunResults" xl="6" md="12" class="mb-r col-with-logs">
          <modal-card
            :message="stdLogs"
            title="Standard Logs from Algorithm"
            :clearPossibility="false"
          />
        </mdb-col>
        <mdb-col v-show="showRunResults" xl="6" md="12" class="mb-r col-with-logs">
          <modal-card
            :message="dimacs_str"
            title="Dimacs SAT Encoding of the Problem"
            :clearPossibility="false"
          />
        </mdb-col>
        <mdb-col v-show="showSudoku" xl="6" md="12" class="mb-r col-with-logs">
          <modal-card
            :message="sudoku"
            title="Sudoku"
            :clearPossibility="false"
          />
        </mdb-col>
      </mdb-row>
    </section>
  </section>
</template>

<script src="@/assets/js/sudoku.js" />
<style scoped src="@/assets/styles/nqueens.css" />
