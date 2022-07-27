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
import benchmark_communication from '@/assets/js/benchmark_communication'

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
      showRunResults: false,
      isCustomRunRunning: false,
      isBenchmarkRunning: false,
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
        this.isCustomRunRunning = false
      }
      this.redisErrorLogs = redisErrorLogs
      this.redisStdLogs = redisStdLogs
      this.stdLogs = stdLogs
    },
    async pollRunningBenchmark(algo, bench) {
      let data = await benchmark_communication.fetch_benchmark_progress(this.serverAddress, algo, bench)
      if (data.result === 'failure' || data.result == 100) {
        clearInterval(this.pollingInterval)
        this.isBenchmarkRunning = false
      }
    },
    startMonitoringCustomRun(algo, bench, benchIn) {
      this.isCustomRunRunning = true
      this.pollingInterval = setInterval(this.pollCustomRun.bind(this, algo, bench, benchIn), 1000)
    },
    startMonitoringBenchmark(algo, bench) {
      this.pollingInterval = setInterval(this.pollRunningBenchmark.bind(this, algo, bench), 1000)
    },
    async runButtonClicked(algo, bench, benchIn, logLevel) {
      if (this.runButtonText === "Stop") {
        return
      }
      this.showRunResults = true
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
      return [data.benchmarks, data.algorithms, data.running_job]
    },
    async fetchCustomRunLogs(serverAddress) {
      let data = await fetch(`${serverAddress}/custom_run/get_logs`)
        .then(response => response.json())
      return data.result
    },
    async fetchInfoFromServer() {
      let [benchmarks, algorithms, running_job] = await this.fetchBasicInfoFromServer(this.serverAddress)
      let [running_algo, running_bench] = await benchmark_communication.fetch_running_benchmark(this.serverAddress)
      if (running_algo != "none") {
        this.isBenchmarkRunning = true
        this.startMonitoringBenchmark(running_algo, running_bench)
      } else {
        this.isBenchmarkRunning = false
      }
      this.benchmarks = benchmarks
      this.algorithms = algorithms
      if (running_job.algorithm !== "none") {
        this.selectedAlgorithmName      = running_job.algorithm
        this.selectedBenchmarkName      = running_job.benchmark
        this.selectedBenchmarkInputName = running_job.entry
        this.showRunResults             = true
        this.startMonitoringCustomRun(
          this.selectedAlgorithmName,
          this.selectedBenchmarkName,
          this.selectedBenchmarkInputName
        )
      }
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
      if (this.isCustomRunRunning) {
        return "Stop"
      } else {
        return "Run"
      }
    },
    runButtonClass: function() {
      if (this.isCustomRunRunning) { 
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
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  }
}