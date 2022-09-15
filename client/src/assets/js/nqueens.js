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

import benchmark_communication from '@/assets/js/benchmark_communication'
import custom_run_communication from '@/assets/js/customRun_communication'
import nqueens_communication from '@/assets/js/nqueens_communication'
import ModalCard from '@/components/ModalCard.vue'
import LogSelector from '@/components/LogSelectorComponent.vue'
import Vue from 'vue'

export default {
  name: 'N-Queens',
  title: 'SAT: N-Queens',
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
    ModalCard,
    LogSelector
  },
  data () {
    let defaultAlgorithmName = "Pick an algorithm"
    return {
      algorithms: [],
      benchmarks: [],
      defaultAlgorithmName: defaultAlgorithmName,
      selectedAlgorithmName: defaultAlgorithmName,
      selectedLogLevels: [
        "WARNING",
      ],
      stopRunFunction: undefined,
      showRunResults: false,
      isOtherTabRunning: false,
      isNQueensRunning: false,
      showBenchmarkInputContent: false,
      benchmarkInputContent: "",
      redisStdLogs: "",
      redisErrorLogs: "",
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
      timeoutCustomRun: 3,
      problem_parameters: undefined,
      chessBoard: {
        data: ""
      },
      dimacs_str: {
        data: ""
      },
      stdLogs: {
        data: ""
      }
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
    async pollRunningNQueens(algo, n, run_as_benchmark, timeout) {
      let is_finished_data = await nqueens_communication.fetchProgress(
        this.serverAddress, algo, n, run_as_benchmark, timeout
      )
      let is_finished = is_finished_data.result
      let stdLogsPacked = await nqueens_communication.fetchStdLogs(
        this.serverAddress, algo, n, run_as_benchmark, timeout
      )
      Vue.set(this.stdLogs, "data", stdLogsPacked.result)
      if (this.dimacs_str.data.length === 0) {
        console.log("fetching data for dimacs str")
        let dimacs = await nqueens_communication.fetchDimacsFile(
          this.serverAddress, n
        )
        if (dimacs.result == "success") {
          console.log("data fetched !")
          Vue.set(this.dimacs_str, "data", "<code>" + dimacs.content + "</code>")
          console.log(this.dimacs_str.data)
        }
      }
      
      if (is_finished === 'failure' || is_finished == "yes") {
        
        clearInterval(this.pollingInterval)
        this.isNQueensRunning = false
        this.stopRunFunction = undefined
        this.pollingInterval = undefined
        if (is_finished == "yes") {
          console.log(is_finished_data.model)
          this.drawChessboard(n, is_finished_data.model)
        }
      }
    },
    async stopRun(algo, n, run_as_benchmark, timeout) {
      nqueens_communication.fetchStop(
        this.serverAddress, algo, n, run_as_benchmark, timeout)
    },
    drawChessboard(n, model=undefined) {
      let chessBoard = ""

      for (let i=0; i<n; i++){
        chessBoard += `<div style="height: 32px; width: ${n * 32}px;">`
        for (let j=0; j<n; j++){
          chessBoard += `<span style="font-size: 28px; display: inline-block; height: 32px; width: 32px; background-color: ${((i + j) % 2) == 0 ? '#5595fb ' : 'white'};">`
          chessBoard += `${(model && model[i * n + j] > 0) ? "<i class=\"fas fa-chess-queen\"></i>" : ""} </span>`
        }
        chessBoard += "</div>"
      }
      Vue.set(this.chessBoard, "data", chessBoard)
    },
    startMonitoringNQueens(algo, n, run_as_benchmark, timeout) {
      this.drawChessboard(n)
      Vue.set(this.dimacs_str, "data", "")
      this.isNQueensRunning = true
      this.showRunResults = true
      this.stopRunFunction = this.stopRun.bind(this, algo, n, run_as_benchmark, timeout)
      this.pollingInterval = setInterval(this.pollRunningNQueens.bind(this, algo, n, run_as_benchmark, timeout), 1000)
    },
    startMonitoringCustomRun() {
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
    createParamsDict() {
      let dict = {}
      for (let i = 0; i < this.problem_parameters.length; i++) {
        let param = this.problem_parameters[i]
        dict[param.name] = param.default
      }
      return dict
    },
    async runButtonClicked(algo, logLevel) {
      if (this.runButtonText === "Stop") {
        this.stopRunFunction()
        return
      }
      if ( !algo ) {
        return
      }
      let algoName = this.createAlgorithmName(algo)
      let paramsDict = this.createParamsDict()
      let data = await nqueens_communication.fetchStart(
        this.serverAddress,
        algoName,
        paramsDict.N,
        paramsDict.run_as_benchmark,
        paramsDict.timeout,
        logLevel
        )

      if (data.result !== "success") {
        return
      }
      this.startMonitoringNQueens(algoName,
        paramsDict.N,
        paramsDict.run_as_benchmark,
        paramsDict.timeout
      )
    },
    extractAlgorithmName(algorithmName) {
      return algorithmName.split(';')[0]
    },
    checkOtherRunningServices(custom_run_info, running_algo, running_bench) {
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
    },
    async fetchInfoFromServer() {
      let data = await nqueens_communication.fetchBasicInfoFromServer(this.serverAddress)
      let custom_run_info = await custom_run_communication.fetchRunningCustomRun(this.serverAddress)
      let [running_algo, running_bench] = await benchmark_communication.fetchRunningBenchmark(this.serverAddress)
      if (data.result !== "success") {
        return
      }

      if (data.running_job.algorithm != "none") {
        this.selectedAlgorithmName      = this.extractAlgorithmName(data.running_job.algorithm)
        let options_array = data.running_job.algorithm.split(';')
        let selAlgo = undefined
        for (let k = 0; k < this.algorithms.length; k++) {
          if (this.algorithms[k].name == this.selectedAlgorithmName) {
            selAlgo = this.algorithms[k]
            break
          }
        }
        if (selAlgo) {
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
        }
        this.startMonitoringNQueens(
          data.running_job.algorithm,
          data.running_job.N,
          data.running_job.run_as_benchmark,
          data.running_job.timeout
        )
      }

      this.checkOtherRunningServices(custom_run_info, running_algo, running_bench)
      this.algorithms = data.algorithms
      this.problem_parameters = data.problem_parameters
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
    showRunButton: function() {
      return this.selectedAlgorithmName != this.defaultAlgorithmName
    },
    runButtonText: function() {
      if (this.isNQueensRunning) {
        return "Stop"
      } else {
        return "Run"
      }
    },
    runButtonClass: function() {
      if (this.isNQueensRunning) { 
        return "run-button-stop"
      } else {
        return "run-button-start"
      }
    },
  },
  created() {
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    this.fetchInfoFromServer()
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
    }
  }
}