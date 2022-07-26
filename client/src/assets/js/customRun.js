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
      isCustomInputRunning: false,
      showRunResults: false,
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
    enquiryIfBenchmarkIsRunning() {
      this.isBenchmarkRunning = false
    },
    runButtonClicked(algo, bench, benchIn) {
      this.showRunResults = true;
      this.stdLogs = `<code>STD LOGS: ${algo} is running</code>`
      this.redisStdLogs = `<code>REDIS STD LOGS: ${bench} is running</code>`
      this.redisErrorLogs = `<code>REDIS ERROR LOGS: ${benchIn} is running</code>`
    },
    showInputClicked(bench, benchIn) {
      this.showBenchmarkInputContent = true;
      this.benchmarkInputContent = `<code>Benchmark input content: ${bench}, ${benchIn}</code>`
    },
    fetchInfoFromServer() {
      fetch(`${this.serverAddress}/custom_run/`)
        .then(response => response.json())
        .then(function(data) {
          this.benchmarks = data.benchmarks
          this.algorithms = data.algorithms
        }.bind(this))
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
      return "Run"
    },
    runButtonClass: function() {
      if (this.isCustomInputRunning) {
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
    this.enquiryIfBenchmarkIsRunning()
  }
}