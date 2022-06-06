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
                <p>TASK {{algorithm.task}}</p>
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
                <mdb-btn color="primary" class="runButton" @click="runBenchmarkClicked(algorithm.name,selected[index][0], index)" :disabled="isDisabled">Run</mdb-btn>

                <div class="progress" :style="displayProgressBar(index)">
                  <div aria-valuemax="100" aria-valuemin="0" :aria-valuenow="progressBarValue" class="progress-bar bg-primary" role="progressbar"
                    :style="progressBarStyle"></div>
                </div>
              </mdb-container>
            </mdb-card-body>
          </mdb-card>
        </mdb-col>
      </mdb-row>
    </section>
  </section>
</template>

<script>
import {
    mdbBtn,
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardBody,
    mdbIcon,
    mdbCardTitle,
    mdbContainer,
    mdbView
} from 'mdbvue'

export default {
  name: 'Dashboard',
  components: {
    mdbBtn,
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardBody,
    mdbCardTitle,
    mdbIcon,
    mdbContainer,
    mdbView
  },
  data () {
    return {
      showFrameModalTop: false,
      showFrameModalBottom: false,
      showSideModalTopRight: false,
      showSideModalTopLeft: false,
      showSideModalBottomRight: false,
      showSideModalBottomLeft: false,
      showCentralModalSmall: false,
      showCentralModalMedium: false,
      showCentralModalLarge: false,
      showCentralModalFluid: false,
      showFluidModalRight: false,
      showFluidModalLeft: false,
      showFluidModalTop: false,
      showFluidModalBottom: false,

      benchmarks: [
        'firstBenchmark',
        'secondBenchmark',
        '3Benchmark',
        '4Benchmark',
        '5Benchmark',
        '6Benchmark',
        '7Benchmark',
        '8Benchmark',
        '9Benchmark',
        '10Benchmark',
      ],
      algorithms: [
        {
          name: 'DPPL',
          task: '2'
        },
        {
          name: 'Watched Literals',
          task: '3'
        },
        {
          name: 'CDCL',
          task: '4'
        },
        {
          name: 'Decision Heuristics',
          task: '5'
        },
        {
          name: 'Look-Ahead Solver',
          task: '6'
        }
      ],
      symbolsForAlgorithms: [
        'cat',
        'crow',
        'dove',
        'dragon',
        'hippo'
      ],
      // need to render dynamically
      selected: [
        [], [], [], [], []
      ],
      runningComputation: false,
      runComputationFor: 3000,
      runningIndex: null,
      computationRuntime: 0,
      progressBarValue: 0,
      progressBarStyle: "width: 0%"
    }
  },
  methods: {
    runBenchmarkClicked(algorithmName, selectedBenchmark, selectedIndex) {
      if (!algorithmName || !selectedBenchmark) {
        return
      }
      this.runningComputation = true
      this.start = new Date()
      this.runningIndex = selectedIndex
      this.pollingInterval = setInterval(this.pollComputation.bind(this), 1000)
    },
    resetPollingParameters() {
      this.start = null
      this.runningIndex = null
      this.runningComputation = false
      this.computationRuntime = 0
    },
    pollComputation() {
      let current = new Date()
      this.computationRuntime = current.getTime() - this.start.getTime()
      if (this.computationRuntime > this.runComputationFor) {
        clearInterval(this.pollingInterval)
        this.resetPollingParameters()
      }
    },
    displayProgressBar(index) {
      if (index === this.runningIndex) {
        return ""
      } else {
        return "display: none;"
      }
    },
  },
  computed: {
    isDisabled() {
      return this.runningComputation;
    },
    getComputationRuntime: {
      get() {
        return this.computationRuntime
      },
      set(value) {
        this.computationRuntime = value
      }
    },
  },
  watch: {
    computationRuntime: {
      handler(newValue) {
        let percent = newValue * 100 / this.runComputationFor
        this.progressBarValue = percent
        this.progressBarStyle = `width: ${percent}%`
      },
      immediate: true
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.cascading-admin-card {
  margin: 20px 0;
}
.cascading-admin-card .admin-up {
  margin-left: -20px;
  margin-right: 4%;
  margin-top: -20px;
}
.cascading-admin-card .admin-up .fas,
.cascading-admin-card .admin-up .far {
  box-shadow: 0 2px 9px 0 rgba(0, 0, 0, 0.2), 0 2px 13px 0 rgba(0, 0, 0, 0.19);
  padding: 1.2rem;
  font-size: 2.8rem;
  color: #fff;
  text-align: left;
  margin-right: 0.5rem;
  border-radius: 5px;
}
.cascading-admin-card .admin-up .algorithmName {
  position: absolute;
  top: 38%;
  left: 55%;
  transform: translateX(-50%) translateY(-0%);
}
.cascading-admin-card .admin-up .taskNumber {
  float: right;
  margin-top: -3rem;
  text-align: right;
}
.admin-up .taskNumber p {
  color: #999999;
  font-size: 12px;
}

.cascading-admin-card .benchmarkSelector {
  color: #999999;
  margin-bottom: -0.05rem;
  font-size: 13px;
}

.cascading-admin-card .benchmarkPossibilities {
  color: #1f71ff;
  font-size: 12px;
  padding: 0.1rem;
}

.cascading-admin-card .runButton {
  margin-left: 40%;
  margin-top: 1rem;
}

.cascading-admin-card .progress {
  margin-top: 0.5rem;
}

.classic-admin-card .card-body {
  color: #fff;
  margin-bottom: 0;
  padding: 0.9rem;
}
.classic-admin-card .card-body p {
  font-size: 13px;
  opacity: 0.7;
  margin-bottom: 0;
}
.classic-admin-card .card-body h4 {
  margin-top: 10px;
}
</style>
