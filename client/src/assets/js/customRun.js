import {
  mdbCard,
  mdbCardBody,
  mdbCardTitle,
  mdbRow,
  mdbCol,
  mdbView,
  mdbIcon,
  mdbContainer,
  mdbBtn,
  mdbScrollbar,
} from 'mdbvue'

import redis_logs from '@/assets/js/get_redis_logs'

export default {
  name: 'CustomRun',
  components: {
    mdbCard,
    mdbCardBody,
    mdbCardTitle,
    mdbRow,
    mdbCol,
    mdbView,
    mdbIcon,
    mdbContainer,
    mdbBtn,
    mdbScrollbar,
  },
  data () {
    let defaultBenchmarkName = "Pick a benchmark"
    let defaultAlgorithmName = "Pick an algorithm"
    let defaultBenchmarkInputName = "Pick a benchmark input"
    return {
      algorithms: [],
      benchmarks: [],
      defaultBenchmarkInputName: defaultBenchmarkInputName,
      selectedBenchmarkInputName: defaultBenchmarkInputName,
      customInputName: "Type custom input",
      defaultAlgorithmName: defaultAlgorithmName,
      selectedAlgorithmName: defaultAlgorithmName,
      defaultBenchmarkName: defaultBenchmarkName,
      selectedBenchmarkName: defaultBenchmarkName,
      selectedLogLevel: "WARNING",
      isCustomInputRunning: false,
      showRunResults: false,
      showBenchmarkInputContent: false,
      benchmarkInputContent: "",
      redisStdLogs: "",
      redisErrorLogs: "",
      stdLogs: "",
    };
  },
  methods: {
    findCorrespondingName(array, name) {
      for (let i = 0; i < array.length; i++) {
        if (array[i].name === name) {
          return array[i]
        }
      }
      return null
    },
    enquiryIfBenchmarkIsRunning() {
      this.isBenchmarkRunning = false
    },
    async fetchStart(algo, bench, benchIn, logLevel) {
      return await fetch(`${this.serverAddress}/custom_run/start`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          algorithm:  algo,
          benchmark:  bench,
          entry:      benchIn,
          logLevel:   logLevel
        })
      }).then(response => response.json())
    },
    async pollCustomRun(algo, bench, benchIn) {
      let [redisErrorLogs, redisStdLogs] = await redis_logs.fetch(this.serverAddress)
      let stdLogs = await this.fetchCustomRunLogs(this.serverAddress)
      let is_finished = await this.fetchProgress(this.serverAddress, algo, bench, benchIn)
      if (redisErrorLogs  === 'failure' ||
          stdLogs         === 'failure' ||
          is_finished     === 'failure' ||
          is_finished     === "yes") {
        clearInterval(this.pollingInterval)
        this.pollingInterval = undefined;
      }
      this.redisErrorLogs = redisErrorLogs
      this.redisStdLogs = redisStdLogs
      this.stdLogs = stdLogs
    },
    startMonitoringCustomRun(algo, bench, benchIn) {
      this.pollingInterval = setInterval(this.pollCustomRun.bind(this, algo, bench, benchIn), 1000)
    },
    async runButtonClicked(algo, bench, benchIn, logLevel) {
      this.showRunResults = true;
      this.startedAlgo = `${algo},${bench},${benchIn}`
      if ( !algo || !bench || !benchIn) {
        return
      }
      let data = await this.fetchStart(algo, bench, benchIn, logLevel)

      if (data.result !== "success") {
        return
      }
      this.startMonitoringCustomRun(algo, bench, benchIn)
    },
    showInputClicked(bench, benchIn) {
      this.showBenchmarkInputContent = true;
      this.benchmarkInputContent = `<code>Benchmark input content: ${bench}, ${benchIn}</code>`
    },
    async fetchProgress(serverAddress, algo, bench, benchIn) {
      let data = null
      try {
        data = await fetch(`${serverAddress}/custom_run/is_finished`, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            algorithm:  algo,
            benchmark:  bench,
            entry:      benchIn
          })
        }).then(response => response.json())
      } catch {
        data = {
          result: 'failure'
        }
      }
      return data.result
    },
    async fetchBasicInfoFromServer(serverAddress) {
      let data = await fetch(`${serverAddress}/custom_run/`)
        .then(response => response.json())
      return [data.benchmarks, data.algorithms]
    },
    async fetchCustomRunLogs(serverAddress) {
      let data = await fetch(`${serverAddress}/custom_run/get_logs`)
        .then(response => response.json())
      return data.result
    },
    async fetchInfoFromServer() {
      let [benchmarks, algorithms] = await this.fetchBasicInfoFromServer(this.serverAddress)
      this.benchmarks = benchmarks
      this.algorithms = algorithms
    }
  },
  computed: {
    selectedAlgorithm: function() {
      let algo = this.findCorrespondingName(this.algorithms, this.selectedAlgorithmName)
      if (algo)  {
        return algo
      }
      return {
        name: this.selectedAlgorithmName,
        taskName: "TASK --none--"
      }
    },
    selectedBenchmark: function() {
      let bench = this.findCorrespondingName(this.benchmarks, this.selectedBenchmarkName)
      if (bench) {
        return bench
      }
      return {
        name: this.selectedBenchmarkName,
        inputs: []
      }
    },
    showBenchmarkInputs: function() {
      return this.selectedBenchmark.inputs.length > 0
    },
    showCustomInputForm: function() {
      return this.selectedBenchmark.name === this.customInputName
    },
    showRunButton: function() {
      return this.selectedAlgorithmName != this.defaultAlgorithmName &&
        this.selectedBenchmarkName != this.defaultBenchmarkName && 
        this.selectedBenchmarkInputName != this.defaultBenchmarkInputName &&
        this.selectedBenchmarkInputName != this.customInputName
    },
    runButtonText: function() {
      return "Run"
    },
    runButtonClass: function() {
      if (this.isCustomInputRunning) {
        return "run-button-stop"
      } else {
        return "run-button-start"
      }
    },
  },
  created() {
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    this.fetchInfoFromServer()
    // TODO: custom input
    // this.benchmarks.push({
    //   name: this.customInputName,
    //   inputs: []
    // })
    this.enquiryIfBenchmarkIsRunning()
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  }
}