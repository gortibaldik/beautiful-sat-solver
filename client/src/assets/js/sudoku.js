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
import sudoku_communication from '@/assets/js/sudoku_communication'
import ModalCard from '@/components/ModalCard.vue'
import LogSelector from '@/components/LogSelectorComponent.vue'
import Vue from 'vue'

export default {
  name: 'Sudoku',
  title: 'SAT: Sudoku',
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
      isSudokuRunning: false,
      showBenchmarkInputContent: false,
      benchmarkInputContent: "",
      redisStdLogs: "",
      redisErrorLogs: "",
      displayModal: false,
      modalMessage: "",
      modalTitle: "",
      timeoutCustomRun: 3,
      problem_parameters: undefined,
      chessBoard: "",
      si: -1,
      stdLogs: {
        data: ""
      },
      dimacs_str: {
        data: ""
      },
      sudoku: {
        data: ""
      },
      lastSudoku: "",
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
    async pollRunningSudoku(algo, sudoku) {
      let is_finished_data = await sudoku_communication.fetchProgress(this.serverAddress, algo)
      let is_finished = is_finished_data.result
      let stdLogsPacked = await sudoku_communication.fetchStdLogs(this.serverAddress, algo)
      Vue.set(this.stdLogs, "data", stdLogsPacked.result)
      if (this.dimacs_str.data.length === 0) {
        console.log("fetching data for dimacs str")
        let dimacs = await sudoku_communication.fetchDimacsFile(
          this.serverAddress, algo, sudoku
        )
        if (dimacs.result == "success") {
          console.log("data fetched !")
          Vue.set(this.dimacs_str, "data", "<code>" + dimacs.content + "</code>")
          console.log(this.dimacs_str.data)
        }
      }
      
      if (is_finished === 'failure' || is_finished == "yes") {
        
        clearInterval(this.pollingInterval)
        this.isSudokuRunning = false
        this.stopRunFunction = undefined
        this.pollingInterval = undefined
        if (is_finished == "yes") {
          console.log(is_finished_data.model)
          // DRAW SUDOKU
          this.createSudokuTable(sudoku, is_finished_data.model)
        }
      }
    },
    async stopRun(algo) {
      sudoku_communication.fetchStop(
        this.serverAddress, algo)
    },
    startMonitoringSudoku(algo, sudoku) {
      Vue.set(this.dimacs_str, "data", "")
      this.isSudokuRunning = true
      this.showRunResults = true
      this.stopRunFunction = this.stopRun.bind(this, algo)
      this.pollingInterval = setInterval(this.pollRunningSudoku.bind(this, algo, sudoku), 1000)
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
      let data = await sudoku_communication.fetchStart(
        this.serverAddress,
        algoName,
        paramsDict.Sudoku,
        logLevel
        )

      if (data.result !== "success") {
        return
      }
      this.startMonitoringSudoku(algoName, paramsDict.Sudoku)
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
      let data = await sudoku_communication.fetchBasicInfoFromServer(this.serverAddress)
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
        this.startMonitoringSudoku(data.running_job.algorithm)
      }

      this.checkOtherRunningServices(custom_run_info, running_algo, running_bench)
      this.algorithms = data.algorithms
      this.problem_parameters = data.problem_parameters
      this.si = this.findSudokuIndex()
      this.di = this.findDifficultyIndex()
    },
    findSudokuIndex() {
      for (let i = 0; i < this.problem_parameters.length; i++) {
        if (this.problem_parameters[i].name == 'Sudoku') {
          return i
        }
      }
      return -1
    },
    findDifficultyIndex() {
      for (let i = 0; i < this.problem_parameters.length; i++) {
        if (this.problem_parameters[i].name == 'difficulty') {
          return i
        }
      }
      return -1
    },
    async generateSudokuClicked() {
      if (this.si == -1) {
        return
      }
      let problem_parameter = this.problem_parameters[this.si]
      this.lastSudoku = this.sudoku.data
      if (this.sudoku.data == "") {
        this.sudoku.data = "_"
      }
      let sudoku = await sudoku_communication.fetchGenerateSudoku(
        this.serverAddress,
        this.problem_parameters[this.di].default
      )
      problem_parameter.default = sudoku
      Vue.set(this.problem_parameters, this.si, problem_parameter)
    },
    createSudokuTable(sudoku, model=undefined) {
      let rows = sudoku.trim().split('\n')
      let html = `<table style="background-color: #7faaf0;">`
      for (let r = 0; r < 9; r++) {
        html += "<tr>"
        let columns = rows[r].trim().split(' ')
        for (let c = 0; c < 9; c++) {
          if (columns[c] == "_") {
            html += `<td style="background-color: #d2ddff; padding: 3px; padding-left: 10px; padding-right: 10px; border-style: solid; border-width: 1px;">`
            if (! model) {
              html += " "
            } else {
              let first = r * 81 + c * 9
              for (let v = 1; v < 10; v++) {
                if (model[first + v - 1] > 0) {
                  html += `${v}`
                }
              }
            }
            html += `</td>`
          } else {
            html += `<td style="padding: 3px; padding-left: 10px; padding-right: 10px; border-style: solid; border-width: 1px;">${columns[c]}</td>`
          }
        }
        html += "</tr>"
      }
      html += "</table>"
      Vue.set(this.sudoku, "data", html)
    }
  },
  computed: {
    generateAgain() {
      return this.sudoku.data == "" || this.sudoku.data != this.lastSudoku
    },
    showSudoku: function() {
      if (! this.problem_parameters) {
        return false
      }
      let sudoku = this.problem_parameters[this.si].default
      if (sudoku.length > 0) {
        let rows = sudoku.trim().split('\n')
        if (rows.length != 9) {
          console.log(`rows: ${rows.length}`)
          return false
        }
        for (let i = 0; i < 9; i++) {
          let columns = rows[i].trim().split(' ')
          if (columns.length != 9) {
            console.log(`columns: ${columns.length}`)
            return false
          }
        }
        this.createSudokuTable(sudoku)
        return true
      }
      return false
    },
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
      if (this.isSudokuRunning) {
        return "Stop"
      } else {
        return "Run"
      }
    },
    runButtonClass: function() {
      if (this.isSudokuRunning) { 
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