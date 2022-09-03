import {
  mdbBtn,
  mdbRow,
  mdbCol,
  mdbCard,
  mdbCardBody,
  mdbIcon,
  mdbCardTitle,
  mdbContainer,
  mdbView,
  mdbModalTitle,
  mdbModalBody,
  mdbModal,
  mdbModalHeader,
  mdbModalFooter,
} from 'mdbvue'

import Vue from 'vue'
import custom_run_comm from '@/assets/js/customRun_communication'
import benchmark_comm from '@/assets/js/benchmark_communication'

export default {
  name: 'Dashboard',
  title: 'SAT: Benchmarks',
  components: {
    mdbBtn,
    mdbRow,
    mdbCol,
    mdbCard,
    mdbCardBody,
    mdbCardTitle,
    mdbIcon,
    mdbContainer,
    mdbView,
    mdbModalTitle,
    mdbModalBody,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter
  },
  data () {
    return {
      benchmarks: [],
      algorithms: [],
      symbolsForAlgorithms: [
        'cat',
        'crow',
        'dove',
        'dragon',
        'hippo'
      ],
      selected: [],
      displayedModalButtons: [],
      displayedModalButtonsBenchmarks: [],
      displayedModals: [],
      displayedModalButtonTimeouts: [],
      modalMessages: [],
      selectedLogLevels: [],
      serverAddress: "",
      allBenchmarksAreRunning: false,
      runningComputation: false,
      runningIndex: null,
      runningBenchmark: null,
      progressOfAlgorithm: 0,
      progressBarValue: 0,
      progressBarStyle: "width: 0%",
      displayModalFor: 0, // will be populated from backend
      isCustomRunRunning: false,
      customRunInterval: undefined,
      pollTimeoutValue: 1000,
    }
  },
  methods: {
    //#region INITIALIZATION
    populatePlaceholders() {
      let s = []
      let dmb = []
      let dmbb = []
      let dm = []
      let mm = []
      let dmto = []
      let sll = []
      for (let i = 0; i < this.algorithms.length; i++) {
        s.push([])
        dmb.push(null)
        dmbb.push("")
        dm.push(false)
        mm.push("")
        dmto.push(null)
        sll.push("WARNING")
      }
      this.selected = s
      this.displayedModalButtons = dmb
      this.displayedModalButtonsBenchmarks = dmbb
      this.displayedModals = dm
      this.modalMessages = mm
      this.displayedModalButtonTimeouts = dmto
      this.selectedLogLevels = sll
    },
    async getAlgorithms() {
      let data = await benchmark_comm.fetchBenchmarks(this.serverAddress)
      if (data["result"] === "failure") {
        return
      }
      this.algorithms = this.extractAlgorithmNamesFromResponse(data)
      this.displayModalFor = data["benchmarked_result_availability"]
      this.populatePlaceholders()
      this.benchmarks = data["benchmarks"]
      this.restartMonitorings(data["benchmarkable_algorithms_running_status"])
      this.populatePlaceholders()
    },
    restartMonitorings(running_statuses) {
      for (let i = 0; i < running_statuses.length; i++) {
        if (running_statuses[i].running) {
          this.runningAlgorithm = this.algorithms[i].name
          if (running_statuses[i].options.length > 0) {
            this.runningAlgorithm += ';' + running_statuses[i].options
          }
          console.log(`FOUND RUNNING ALGORITHM: ${this.runningAlgorithm}`)
          if (running_statuses[i].all) {
            this.startMonitoringProgressAll(this.runningAlgorithm, i)
          } else {
            this.startMonitoringProgress(this.runningAlgorithm, running_statuses[i].benchmarkName, i)
            Vue.set(this.selected, i, [running_statuses[i].benchmarkName])
          }
          // only one can be running
          let options_array = running_statuses[i].options.split(';')
          for (let j = 0; j < options_array.length; j++) {
            let [option, value] = options_array[j].split('=')
            if (value === "true") {
              value = true
            } else if (value === "false") {
              value = false
            }
            for (let k = 0; k < this.algorithms[i].options.length; k++) {
              if (this.algorithms[i].options[k].name == option) {
                this.algorithms[i].options[k].default = value
                break
              }
            }
          }
          break
        }
      }
    },
    extractAlgorithmNamesFromResponse(response) {
      let algorithmNames = []
      let benchmarkableAlgorithms = response["benchmarkable_algorithms"]
      for (let i = 0; i < benchmarkableAlgorithms.length; i++) {
        algorithmNames.push({
          name: benchmarkableAlgorithms[i].name,
          task: benchmarkableAlgorithms[i].taskName,
          symbol: benchmarkableAlgorithms[i].symbol,
          options: benchmarkableAlgorithms[i].options
        })
      }
      return algorithmNames
    },
    async pollInfoAboutCustomRun() {
      let data = await custom_run_comm.fetchRunningCustomRun(this.serverAddress)
      if (data.result === "failure") {
        console.log("Server failure pollInfoAboutCustomRun")
      }
      if (data.running_job.entry === "none") {
        this.isCustomRunRunning = false
        if (this.customRunInterval) {
          clearInterval(this.customRunInterval)
          this.customRunInterval = undefined
        }
      } else {
        this.isCustomRunRunning = true
      }
    },
    async getInfoAboutCustomRun() {
      await this.pollInfoAboutCustomRun()
      if (this.isCustomRunRunning) {
        this.customRunInterval = setInterval(this.pollInfoAboutCustomRun.bind(this), this.pollTimeoutValue)
      }
    },
    //#endregion INITIALIZATION
    //#region RUN BUTTON
    runButtonIsDisabled(index) {
      return this.runningComputation && index != this.runningIndex;
    },
    runButtonDisplaysStopMessage(index) {
      return this.runningComputation && index == this.runningIndex;
    },
    runButtonText(index) {
      if (this.runButtonDisplaysStopMessage(index)) {
        return "STOP"
      } else {
        return "RUN"
      }
    },
    runButtonColor(index) {
      if (this.runButtonDisplaysStopMessage(index)) {
        return "secondary"
      } else {
        return "primary"
      }
    },
    createAlgorithmName(algorithmName, selectedIndex) {
      let runningAlgorithm = algorithmName
      if (this.algorithms[selectedIndex].options.length > 0) {
        let options = this.algorithms[selectedIndex].options
        for (let i = 0; i < options.length; i++) {
          runningAlgorithm += ';' + options[i].name + '=' + options[i].default
        }
      }
      return runningAlgorithm
    },
    async runBenchmarkClicked(algorithmName, selectedBenchmark, selectedIndex) {
      if (this.allBenchmarksAreRunning) {
        this.clickStopAll(this.runningAlgorithm)
        return
      } else if (this.runButtonDisplaysStopMessage(selectedIndex)) {
        this.clickStopComputation(this.runningAlgorithm, this.runningBenchmark, selectedIndex)
        return
      } else if (!algorithmName || !selectedBenchmark) {
        return
      }
      this.runningAlgorithm = this.createAlgorithmName(algorithmName, selectedIndex)
      this.runningBenchmark = selectedBenchmark
      let data = await benchmark_comm.fetchStartBenchmark(
        this.serverAddress,
        this.runningAlgorithm,
        selectedBenchmark,
        this.selectedLogLevels[selectedIndex]
      )
      if (data['result'] != "success") {
        return
      }
      this.startMonitoringProgress(this.runningAlgorithm, selectedBenchmark, selectedIndex)
    },
    async runAllClicked(algorithmName, selectedIndex) {
      if (!algorithmName) {
        return
      }
      this.runningAlgorithm = this.createAlgorithmName(algorithmName, selectedIndex)
      let data = await benchmark_comm.fetchStartAll(
        this.serverAddress,
        this.runningAlgorithm,
        this.selectedLogLevels[selectedIndex]
      )
      if (data['result'] === "failure") {
        return
      }
      this.startMonitoringProgressAll(this.runningAlgorithm, selectedIndex)
    },
    startMonitoringProgressAll(algorithmName, selectedIndex) {
      this.allBenchmarksAreRunning = true
      this.runningComputation = true
      this.runningIndex = selectedIndex
      this.runningBenchmark = ""

      // switch off the modal button
      if (this.displayedModalButtons[this.runningIndex]) {
        Vue.set(this.displayedModalButtons, this.runningIndex, false)
        clearTimeout(this.displayedModalButtonTimeouts[this.runningIndex])
      }
      this.pollingInterval = setInterval(this.pollAllRun.bind(this, algorithmName), this.pollTimeoutValue)
    },
    startMonitoringProgress(algorithmName, selectedBenchmark, selectedIndex) {
      this.runningComputation = true
      this.runningIndex = selectedIndex
      this.runningBenchmark = selectedBenchmark
      // switch off the modal button
      if (this.displayedModalButtons[this.runningIndex]) {
        Vue.set(this.displayedModalButtons, this.runningIndex, false)
        clearTimeout(this.displayedModalButtonTimeouts[this.runningIndex])
      }
      this.pollingInterval = setInterval(this.pollComputation.bind(this, algorithmName, selectedBenchmark), this.pollTimeoutValue)
    },
    async clickStopComputation(algorithmName, benchmarkName) {
      console.log("stop button clicked")
      let data = await benchmark_comm.fetchStopCommunication(
        this.serverAddress,
        algorithmName,
        benchmarkName
      )
      if (data['result'] === 'failure') {
        console.log("FAILURE ON STOP")
        return
      }
      else {
        clearInterval(this.pollingInterval)
        Vue.set(this.displayedModalButtonsBenchmarks, this.runningIndex, benchmarkName)
        Vue.set(this.displayedModalButtonTimeouts, this.runningIndex, setTimeout(this.cooldownDisplayModalButton.bind(this, this.runningIndex), this.displayModalFor))
        Vue.set(this.displayedModalButtons, this.runningIndex, true)
        this.resetPollingParameters()
      }
    },
    async clickStopAll(algorithmName) {
      let data = await benchmark_comm.fetchStopAll(
        this.serverAddress,
        algorithmName
      )
      if (data['result'] === "failure") {
        console.log("FAILURE ON STOP")
        return
      } else {
        clearInterval(this.pollingInterval)
        this.resetPollingParameters()
      }
    },
    shouldProgressBeDisplayed(index) {
      return index === this.runningIndex
    },
    //#endregion RUN BUTTON
    //#region POLLING COMPUTATION
    resetPollingParameters() {
      this.runningIndex = null
      this.runningComputation = false
      this.progressOfAlgorithm = 0
    },
    async pollComputation(algorithmName, benchmarkName) {
      let data = await benchmark_comm.fetchBenchmarkProgress(
        this.serverAddress,
        algorithmName,
        benchmarkName
      )
      this.progressOfAlgorithm = data['result']
      if (this.progressOfAlgorithm === 'failure') {
        clearInterval(this.pollingInterval)
        this.resetPollingParameters()
      }
      else if (this.progressOfAlgorithm == 100) {
        clearInterval(this.pollingInterval)
        Vue.set(this.displayedModalButtonsBenchmarks, this.runningIndex, benchmarkName)
        Vue.set(this.displayedModalButtonTimeouts, this.runningIndex, setTimeout(this.cooldownDisplayModalButton.bind(this, this.runningIndex), this.displayModalFor))
        Vue.set(this.displayedModalButtons, this.runningIndex, true)
        this.resetPollingParameters()
      }
    },
    async pollAllRun(algorithmName) {
      let data = await benchmark_comm.fetchAllProgress(
        this.serverAddress,
        algorithmName
      )
      if (data['result'] === 'failure' || data['finished']) {
        clearInterval(this.pollingInterval)
        this.resetPollingParameters()
      }
      this.runningBenchmark = data['benchmark_name']
      this.progressOfAlgorithm = data['result']
    },
    //#endregion POLLING COMPUTATION
    //#region BUTTON WITH LOGS
    cooldownDisplayModalButton(indexToSwitchOff) {
      Vue.set(this.displayedModalButtons, indexToSwitchOff, false)
    },
    async clickDisplayModalButton(index) {
      let data = await benchmark_comm.fetchBenchmarkResult(
        this.serverAddress,
        this.runningAlgorithm,
        this.displayedModalButtonsBenchmarks[index]
      )
      if (data['result'] === "failure") {
        return
      }
      Vue.set(this.modalMessages, index, data["result"])
      Vue.set(this.displayedModals, index, true)
    },
    closeModal(index) {
      Vue.set(this.displayedModals, index, false);
    },
    //#endregion BUTTON WITH LOGS
  },
  watch: {
    progressOfAlgorithm: {
      handler(newValue) {
        this.progressBarValue = newValue
        this.progressBarStyle = `width: ${newValue}%`
      },
      immediate: true
    },
  },
  created() {
    //debugger;  // eslint-disable-line no-debugger
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    this.getInfoAboutCustomRun()
    this.getAlgorithms()
  },
  beforeDestroy() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval)
      this.pollingInterval = undefined
    }
    if (this.customRunInterval) {
      clearInterval(this.customRunInterval)
      this.customRunInterval = undefined
    }
  }
}