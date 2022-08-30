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
import nqueens_communication from '@/assets/js/nqueens_communication'

export default {
  name: 'CustomRun',
  title: 'SAT: Custom Run',
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
    let defaultAlgorithmName = "Pick an algorithm"
    return {
      algorithms: [],
      benchmarks: [],
      defaultAlgorithmName: defaultAlgorithmName,
      selectedAlgorithmName: defaultAlgorithmName,
      selectedLogLevel: "WARNING",
      stopRunFunction: undefined,
      showRunResults: false,
      isCustomRunRunning: false,
      isOtherTabRunning: false,
      showBenchmarkInputContent: false,
      benchmarkInputContent: "",
      redisStdLogs: "",
      redisErrorLogs: "",
      stdLogs: "",
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
      timeoutCustomRun: 3,
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
    async pollCustomRun() {
      let data = await custom_run_communication.fetchRunningCustomRun(this.serverAddress)
      if ( data.result === 'failure' ||
           data.running_job.entry === "none") {
        clearInterval(this.pollingInterval)
        this.pollingInterval = undefined;
        this.isOtherTabRunning = false
      }
    },
    async pollRunningBenchmark(algo, bench) {
      let data = await benchmark_communication.fetchBenchmarkProgress(this.serverAddress, algo, bench)
      if (data.result === 'failure' || data.result == 100) {
        clearInterval(this.pollingInterval)
        this.isOtherTabRunning = false
      }
    },
    async pollRunningBenchmarkAll(algo) {
      let data = await benchmark_communication.fetchAllProgress(algo)
      if (data.result === 'failure' || data.finished) {
        clearInterval(this.pollingInterval)
        this.isOtherTabRunning = false
      }
    },
    async stopRun(algo, bench, benchIn) {
      custom_run_communication.fetchStop(this.serverAddress, algo, bench, benchIn)
    },
    startMonitoringCustomRun() {
      this.isCustomRunRunning = true
      this.pollingInterval = setInterval(this.pollCustomRun.bind(this), 1000)
    },
    startMonitoringBenchmark(algo, bench) {
      this.pollingInterval = setInterval(this.pollRunningBenchmark.bind(this, algo, bench), 1000)
    },
    startMonitoringBenchmarkAll(algo) {
      this.pollingInterval = setInterval(this.pollRunningBenchmarkAll.bind(this, algo), 1000)
    },
    createAlgorithmName(algo) {
      let runningAlgorithm = algo.name
      if (algo.options.length > 0) {
        let options = algo.options
        for (let i = 0; i < options.length; i++) {
          runningAlgorithm += ';' + options[i].name + '=' + options[i].default
        }
      }
      return runningAlgorithm
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
      let algoName = this.createAlgorithmName(algo)
      let data = await custom_run_communication.fetchStart(this.serverAddress, algoName, bench, benchIn, logLevel)

      if (data.result !== "success") {
        return
      }
      this.startMonitoringCustomRun(algoName, bench, benchIn)
    },
    async showInputClicked(bench, benchIn) {
      this.showBenchmarkInputContent = true;
      let data = await custom_run_communication.fetchBenchmarkInput(this.serverAddress, bench, benchIn)
      this.benchmarkInputContent = `<code>${data.result}</code>`
    },
    extractAlgorithmName(algorithmName) {
      return algorithmName.split(';')[0]
    },
    async fetchInfoFromServer() {
      let data = await nqueens_communication.fetchBasicInfoFromServer(this.serverAddress)
      let custom_run_info = await custom_run_communication.fetchRunningCustomRun(this.serverAddress)
      let [running_algo, running_bench] = await benchmark_communication.fetchRunningBenchmark(this.serverAddress)
      if (data.result !== "success") {
        return
      }
      if (running_algo != "none") {
        this.isOtherTabRunning = true
        if (running_bench === "__all__") {
          this.startMonitoringBenchmarkAll(running_algo)
        } else {
          this.startMonitoringBenchmark(running_algo, running_bench)
        }
      } else if (custom_run_info.result !== "failure" && custom_run_info.running_job.entry !== "none") {
        this.startMonitoringCustomRun()
      } else { 
        this.isOtherTabRunning = false
      }
      this.algorithms = data.algorithms
    },
    async fetchRedisLogs() {
      let [redisErrorLogs, redisStdLogs] = await redis_logs.fetch(this.serverAddress)
      this.redisErrorLogs = redisErrorLogs
      this.redisStdLogs = redisStdLogs
      return [redisErrorLogs, redisStdLogs]
    },
    async removeStdRedisLogs() {
      await redis_logs.fetch_remove_std(this.serverAddress)
      setTimeout(this.fetchRedisLogs.bind(this), 1000)
    },
    async removeErrorRedisLogs() {
      await redis_logs.fetch_remove_error(this.serverAddress)
      setTimeout(this.fetchRedisLogs.bind(this), 1000)
    },
  },
  computed: {
    selectedAlgorithm: function() {
      let algo = this.findCorrespondingName(this.algorithms, this.selectedAlgorithmName)
      if (algo)  {
        return algo
      }
      return {
        name: this.selectedAlgorithmName,
        taskName: "TASK --none--",
        options: []
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
    showBenchmarkInputButton: function() {
      return this.selectedBenchmarkName != this.defaultBenchmarkName && 
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