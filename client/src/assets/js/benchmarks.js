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
      displayedModals: [],
      displayedModalButtonTimeouts: [],
      modalMessages:[],
      runningComputation: false,
      runningIndex: null,
      runningBenchmark: null,
      progressOfAlgorithm: 0,
      progressBarValue: 0,
      progressBarStyle: "width: 0%",
      displayModalFor: 0, // will be populated from backend
    }
  },
  methods: {
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
    runBenchmarkClicked(algorithmName, selectedBenchmark, selectedIndex) {
      if (!algorithmName || !selectedBenchmark) {
        return
      }
      if (this.runButtonDisplaysStopMessage(selectedIndex)) {
        this.clickStopComputation(algorithmName, selectedBenchmark, selectedIndex)
        return
      }
      fetch("http://127.0.0.1:5000/start_algorithm", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({algorithm: algorithmName, benchmark: selectedBenchmark})
      })
        .then(response => response.json())
        .then(function(data) {
          if (data['result'] != "success") {
            return
          }
          this.startMonitoringProgress(algorithmName, selectedBenchmark, selectedIndex)
        }.bind(this))
    },
    resetPollingParameters() {
      this.runningIndex = null
      this.runningComputation = false
      this.progressOfAlgorithm = 0
    },
    pollComputation(algorithmName, benchmarkName) {
      // here call to the backend 
      fetch("http://127.0.0.1:5000/get_progress", {
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
            Vue.set(this.displayedModalButtonTimeouts, this.runningIndex, setTimeout(this.cooldownDisplayModalButton.bind(this, this.runningIndex), this.displayModalFor))
            Vue.set(this.displayedModalButtons, this.runningIndex, true)
            this.resetPollingParameters()
          }
        }.bind(this))
    },
    clickStopComputation(algorithmName, benchmarkName) {
      fetch("http://127.0.0.1:5000/stop_algorithm", {
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
            Vue.set(this.displayedModalButtonTimeouts, this.runningIndex, setTimeout(this.cooldownDisplayModalButton.bind(this, this.runningIndex), this.displayModalFor))
            Vue.set(this.displayedModalButtons, this.runningIndex, true)
            this.resetPollingParameters()
          }
        }.bind(this))
    },
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
      fetch("http://127.0.0.1:5000/get_result", {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({algorithm: this.algorithms[index].name, benchmark: this.runningBenchmark})
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
    displayProgressBar(index) {
      if (index === this.runningIndex) {
        return ""
      } else {
        return "display: none;"
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
    getAlgorithms() {
      fetch("http://127.0.0.1:5000/benchmarks")
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
    populatePlaceholders() {
      let s = []
      let dmb = []
      let dm = []
      let mm = []
      let dmto = []
      for (let i = 0; i < this.algorithms.length; i++) {
        s.push([])
        dmb.push(null)
        dm.push(false)
        mm.push("")
        dmto.push(null)
      }
      this.selected = s
      this.displayedModalButtons = dmb
      this.displayedModals = dm
      this.modalMessages = mm
      this.displayedModalButtonTimeouts = dmto
    },
    restartMonitorings(running_statuses) {
      for (let i = 0; i < running_statuses.length; i++) {
        if (running_statuses[i].running) {
          this.startMonitoringProgress(this.algorithms[i].name, running_statuses[i].benchmarkName, i)
          Vue.set(this.selected, i, [running_statuses[i].benchmarkName])
        }
      }
    },
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
    }
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
    this.getAlgorithms()
  }
}