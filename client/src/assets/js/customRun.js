import {
  mdbCard,
  mdbCardBody,
  mdbCardTitle,
  mdbRow,
  mdbCol,
  mdbView,
  mdbIcon,
  mdbContainer,
  mdbScrollbar,
  mdbModal,
  mdbModalHeader,
  mdbModalFooter,
  mdbModalBody,
  mdbBtn,
  mdbModalTitle,
} from 'mdbvue'

import redis_logs from '@/assets/js/get_redis_logs'
import benchmark_communication from '@/assets/js/benchmark_communication'
import custom_run_communication from '@/assets/js/customRun_communication'

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
    mdbScrollbar,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter,
    mdbModalBody,
    mdbBtn,
    mdbModalTitle,
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
      stopRunFunction: undefined,
      showRunResults: false,
      isCustomRunRunning: false,
      isBenchmarkRunning: false,
      showBenchmarkInputContent: false,
      benchmarkInputContent: "",
      redisStdLogs: "",
      redisErrorLogs: "",
      stdLogs: "",
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
    };
  },
  methods: {
    switchOnModalRedisStd() {
      console.log("REDIS STD !")
      this.displayModal = true
      this.modalMessage = this.redisStdLogs
      this.modalTitle = "Standard Logs from Algorithm"
    },
    switchOnModalRedisError() {
      console.log("REDIS ERROR !")
      this.displayModal = true
      this.modalMessage = this.redisErrorLogs
      this.modalTitle = "Error Redis Worker Logs"
    },
    switchOnModalStd() {
      console.log("STD !")
      this.displayModal = true
      this.modalMessage = this.stdLogs
      this.modalTitle = "Standard Redis Worker Logs"
    },
    findCorrespondingName(array, name) {
      for (let i = 0; i < array.length; i++) {
        if (array[i].name === name) {
          return array[i]
        }
      }
      return null
    },
    async pollCustomRun(algo, bench, benchIn) {
      let [redisErrorLogs, redisStdLogs] = await redis_logs.fetch(this.serverAddress)
      let stdLogs = await custom_run_communication.fetchCustomRunLogs(this.serverAddress)
      let is_finished = await custom_run_communication.fetchProgress(this.serverAddress, algo, bench, benchIn)
      if (redisErrorLogs  === 'failure' ||
          stdLogs         === 'failure' ||
          is_finished     === 'failure' ||
          is_finished     === "yes") {
        clearInterval(this.pollingInterval)
        this.pollingInterval = undefined;
        this.isCustomRunRunning = false
        this.stopRunFunction = undefined
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
    async stopRun(algo, bench, benchIn) {
      custom_run_communication.fetchStop(this.serverAddress, algo, bench, benchIn)
    },
    startMonitoringCustomRun(algo, bench, benchIn) {
      this.isCustomRunRunning = true
      this.stopRunFunction = this.stopRun.bind(this, algo, bench, benchIn)
      this.pollingInterval = setInterval(this.pollCustomRun.bind(this, algo, bench, benchIn), 1000)
    },
    startMonitoringBenchmark(algo, bench) {
      this.pollingInterval = setInterval(this.pollRunningBenchmark.bind(this, algo, bench), 1000)
    },
    async runButtonClicked(algo, bench, benchIn, logLevel) {
      if (this.runButtonText === "Stop") {
        this.stopRunFunction()
        return
      }
      this.showRunResults = true
      if ( !algo || !bench || !benchIn) {
        return
      }
      let data = await custom_run_communication.fetchStart(this.serverAddress, algo, bench, benchIn, logLevel)

      if (data.result !== "success") {
        return
      }
      this.startMonitoringCustomRun(algo, bench, benchIn)
    },
    showInputClicked(bench, benchIn) {
      this.showBenchmarkInputContent = true;
      this.benchmarkInputContent = `<code>Benchmark input content: ${bench}, ${benchIn}</code>`
    },
    async fetchInfoFromServer() {
      let [benchmarks, algorithms, running_job] = await custom_run_communication.fetchBasicInfoFromServer(this.serverAddress)
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