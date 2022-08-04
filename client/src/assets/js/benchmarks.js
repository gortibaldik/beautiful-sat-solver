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
    mdbView,
    mdbModalTitle,
    mdbModalBody,
    mdbModal,
    mdbModalHeader,
    mdbModalFooter
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
      runningComputation: false,
      runningIndex: null,
      runningBenchmark: null,
      progressOfAlgorithm: 0,
      progressBarValue: 0,
      progressBarStyle: "width: 0%",
      displayModalFor: 0, // will be populated from backend
      isCustomRunRunning: false,
      customRunInterval: undefined,
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
    getAlgorithms() {
      fetch(`${this.serverAddress}/benchmarks/`)
        .then(response => response.json())
        .then(function(data) {
          if (data["result"] === "failure") {
            return
          }
          this.algorithms = this.extractAlgorithmNamesFromResponse(data)
          this.displayModalFor = data["benchmarked_result_availability"]
          this.populatePlaceholders()
          this.benchmarks = data["benchmarks"]
          this.restartMonitorings(data["benchmarkable_algorithms_running_status"])
        }.bind(this))
        .then(() => this.populatePlaceholders())
    },
    restartMonitorings(running_statuses) {
      for (let i = 0; i < running_statuses.length; i++) {
        if (running_statuses[i].running) {
          this.startMonitoringProgress(this.algorithms[i].name, running_statuses[i].benchmarkName, i)
          Vue.set(this.selected, i, [running_statuses[i].benchmarkName])
        }
      }
    },
    extractAlgorithmNamesFromResponse(response) {
      let algorithmNames = []
      let benchmarkableAlgorithms = response["benchmarkable_algorithms"]
      for (let i = 0; i < benchmarkableAlgorithms.length; i++) {
        algorithmNames.push({
          name: benchmarkableAlgorithms[i].name,
          task: benchmarkableAlgorithms[i].taskName
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
        this.customRunInterval = setInterval(this.pollInfoAboutCustomRun.bind(this), 1000)
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
    runBenchmarkClicked(algorithmName, selectedBenchmark, selectedIndex) {
      if (!algorithmName || !selectedBenchmark) {
        return
      }
      if (this.runButtonDisplaysStopMessage(selectedIndex)) {
        this.clickStopComputation(algorithmName, selectedBenchmark, selectedIndex)
        return
      }
      fetch(`${this.serverAddress}/benchmarks/start`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          algorithm: algorithmName,
          benchmark: selectedBenchmark,
          logLevel: this.selectedLogLevels[selectedIndex]
        })
      })
        .then(response => response.json())
        .then(function(data) {
          if (data['result'] != "success") {
            return
          }
          this.startMonitoringProgress(algorithmName, selectedBenchmark, selectedIndex)
        }.bind(this))
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
      this.pollingInterval = setInterval(this.pollComputation.bind(this, algorithmName, selectedBenchmark), 1000)
    },
    clickStopComputation(algorithmName, benchmarkName) {
      fetch(`${this.serverAddress}/benchmarks/stop`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({algorithm: algorithmName, benchmark: benchmarkName})
      }).then(response => response.json())
        .then(function(data) {
          if (data['result'] === 'failure') {
            return
          }
          else {
            clearInterval(this.pollingInterval)
            Vue.set(this.displayedModalButtonsBenchmarks, this.runningIndex, benchmarkName)
            Vue.set(this.displayedModalButtonTimeouts, this.runningIndex, setTimeout(this.cooldownDisplayModalButton.bind(this, this.runningIndex), this.displayModalFor))
            Vue.set(this.displayedModalButtons, this.runningIndex, true)
            this.resetPollingParameters()
          }
        }.bind(this))
    },
    //#endregion RUN BUTTON
    //#region POLLING COMPUTATION
    resetPollingParameters() {
      this.runningIndex = null
      this.runningComputation = false
      this.progressOfAlgorithm = 0
    },
    pollComputation(algorithmName, benchmarkName) {
      // here call to the backend 
      fetch(`${this.serverAddress}/benchmarks/progress`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({algorithm: algorithmName, benchmark: benchmarkName})
      }).then(response => response.json())
        .then(function(data) {
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
        }.bind(this))
    },
    displayProgressBar(index) {
      if (index === this.runningIndex) {
        return ""
      } else {
        return "display: none;"
      }
    },
    //#endregion POLLING COMPUTATION
    //#region BUTTON WITH LOGS
    cooldownDisplayModalButton(indexToSwitchOff) {
      Vue.set(this.displayedModalButtons, indexToSwitchOff, false)
    },
    displayModalButton(index) {
      if (this.displayedModalButtons[index]) {
        return ""
      } else {
        return "display: none;"
      }
    },
    clickDisplayModalButton(index) {
      fetch(`${this.serverAddress}/benchmarks/result`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({algorithm: this.algorithms[index].name, benchmark: this.displayedModalButtonsBenchmarks[index]})
      }).then(response => response.json())
        .then(function(data) {
          if (data['result'] === "failure") {
            return
          }
          Vue.set(this.modalMessages, index, data["result"])
          Vue.set(this.displayedModals, index, true)
        }.bind(this))
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
    }
    if (this.customRunInterval) {
      clearInterval(this.customRunInterval)
    }
  }
}