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

    benchmarks: [
      'firstBenchmark',
      'secondBenchmark',
      '3Benchmark',
      '4Benchmark',
      '5Benchmark',
      '6Benchmark',
      '7Benchmark',
      '8Benchmark',
      '9Benchmark',
      '10Benchmark',
    ],
    algorithms: [
      {
        name: 'DPPL',
        task: '2'
      },
      {
        name: 'Watched Literals',
        task: '3'
      },
      {
        name: 'CDCL',
        task: '4'
      },
      {
        name: 'Decision Heuristics',
        task: '5'
      },
      {
        name: 'Look-Ahead Solver',
        task: '6'
      }
    ],
    symbolsForAlgorithms: [
      'cat',
      'crow',
      'dove',
      'dragon',
      'hippo'
    ],
    // need to fill up dynamically
    // with the same number of defaults
    // as is in algorithms array
    selected: [
      [], [], [], [], []
    ],
    displayedModalButtons: [
      null, null, null, null, null
    ],
    displayedModals: [
      false, false, false, false, false
    ],
    modalMessages:[
      "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
      "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit,",
      "sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam",
      "quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?",
      "At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi",
    ],
    runningComputation: false,
    runComputationFor: 3000,
    runningIndex: null,
    computationRuntime: 0,
    progressBarValue: 0,
    progressBarStyle: "width: 0%",
    displayModalFor: 10000,
  }
},
methods: {
  runBenchmarkClicked(algorithmName, selectedBenchmark, selectedIndex) {
    if (!algorithmName || !selectedBenchmark) {
      return
    }
    // here call to the backend API should be made
    // start the computation
    this.runningComputation = true
    this.start = new Date()
    this.runningIndex = selectedIndex
    this.pollingInterval = setInterval(this.pollComputation, 1000)
  },
  resetPollingParameters() {
    this.start = null
    this.runningIndex = null
    this.runningComputation = false
    this.computationRuntime = 0
  },
  pollComputation() {
    // here call to the backend 
    let current = new Date()
    this.computationRuntime = current.getTime() - this.start.getTime()
    if (this.computationRuntime > this.runComputationFor) {
      clearInterval(this.pollingInterval)
      setTimeout(this.cooldownDisplayModal.bind(this, this.runningIndex), this.displayModalFor)
      Vue.set(this.displayedModalButtons, this.runningIndex, true)
      this.resetPollingParameters()
    }
  },
  cooldownDisplayModal(indexToSwitchOff) {
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
    // there should be loading of modalMessage
    // from backend server
    Vue.set(this.displayedModals, index, true)
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
},
computed: {
  isDisabled() {
    return this.runningComputation;
  },

},
watch: {
  computationRuntime: {
    handler(newValue) {
      let percent = newValue * 100 / this.runComputationFor
      this.progressBarValue = percent
      this.progressBarStyle = `width: ${percent}%`
    },
    immediate: true
  },
}
}