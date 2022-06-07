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