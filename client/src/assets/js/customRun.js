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
      timeoutCustomRun: 3,
    };
  },
  methods: {
    switchOnModalRedisStd() {
      this.displayModal = true
      this.modalMessage = this.redisStdLogs
      this.modalTitle = "Standard Logs from Algorithm"
    },
    switchOnModalRedisError() {
      this.displayModal = true
      this.modalMessage = this.redisErrorLogs
      this.modalTitle = "Error Redis Worker Logs"
    },
    switchOnModalStd() {
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
      // eslint-disable-next-line no-unused-vars
      let [redisErrorLogs, _] = await this.fetchRedisLogs()
      let stdLogs = await custom_run_communication.fetchCustomRunLogs(this.serverAddress)
      let is_finished = await custom_run_communication.fetchProgress(this.serverAddress, algo, bench, benchIn)
      if (redisErrorLogs  === 'failure' ||
      stdLogs         === 'failure' ||
      is_finished     === 'failure' ||
      is_finished     === "yes") {
        if (this.timeoutCustomRun > 0) {
          this.timeoutCustomRun--
        } else {
          clearInterval(this.pollingInterval)
          this.pollingInterval = undefined;
          this.isCustomRunRunning = false
          this.stopRunFunction = undefined
          this.timeoutCustomRun = 3
        }
      }
      this.stdLogs = stdLogs
    },
    async pollRunningBenchmark(algo, bench) {
      let data = await benchmark_communication.fetchBenchmarkProgress(this.serverAddress, algo, bench)
      if (data.result === 'failure' || data.result == 100) {
        clearInterval(this.pollingInterval)
        this.isBenchmarkRunning = false
      }
    },
    async pollRunningBenchmarkAll(algo) {
      let data = await benchmark_communication.fetchAllProgress(algo)
      if (data.result === 'failure' || data.finished) {
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
      let [benchmarks, algorithms, running_job] = await custom_run_communication.fetchBasicInfoFromServer(this.serverAddress)
      let [running_algo, running_bench] = await benchmark_communication.fetchRunningBenchmark(this.serverAddress)
      if (running_algo != "none") {
        this.isBenchmarkRunning = true
        if (running_bench === "__all__") {
          this.startMonitoringBenchmarkAll(running_algo)
        } else {
          this.startMonitoringBenchmark(running_algo, running_bench)
        }
      } else {
        this.isBenchmarkRunning = false
      }
      this.benchmarks = benchmarks
      this.algorithms = algorithms
      if (running_job.algorithm !== "none") {
        this.selectedAlgorithmName      = this.extractAlgorithmName(running_job.algorithm)
        this.selectedBenchmarkName      = running_job.benchmark
        this.selectedBenchmarkInputName = running_job.entry
        this.showRunResults             = true
        let options_array = running_job.algorithm.split(';')
        let selAlgo = undefined
        for (let k = 0; k < this.algorithms.length; k++) {
          if (this.algorithms[k].name == this.selectedAlgorithmName) {
            selAlgo = this.algorithms[k]
            break
          }
        }
        for (let j = 0; j < options_array.length; j++) {
          let [option, value] = options_array[j].split('=')
          if (value === "true") {
            value = true
          } else if (value === "false") {
            value = false
          }
          for (let k = 0; k < selAlgo.options.length; k++) {
            if (selAlgo.options[k].name == option) {
              selAlgo.options[k].default = value
              break
            }
          }
        }
        this.startMonitoringCustomRun(
          running_job.algorithm,
          this.selectedBenchmarkName,
          this.selectedBenchmarkInputName
        )
      }
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