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
        task: "TASK --none--"
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
    this.benchmarks = [
      {
        name: "b1",
        inputs: [
          "i_b1_1",
          "i_b1_2",
          "i_b1_3",
          "i_b1_4"
        ]
      },
      {
        name: "b2",
        inputs: [
          "i_b2_1",
          "i_b2_2",
          "i_b2_3",
          "i_b2_4"
        ]
      },
      {
        name: "b3",
        inputs: [
          "i_b3_1",
          "i_b3_2",
          "i_b3_3",
          "i_b3_4"
        ]
      },
      {
        name: "b4",
        inputs: [
          "i_b4_1",
          "i_b4_2",
          "i_b4_3",
          "i_b4_4"
        ]
      },
      {
        name: "b5",
        inputs: [
          "i_b5_1",
          "i_b5_2",
          "i_b5_3",
          "i_b5_4"
        ]
      },
    ]
    this.algorithms = [
      {
        name: "one",
        task: "TASK 1"
      },
      {
        name: "mouse",
        task: "TASK 2"
      },
      {
        name: "elephant",
        task: "TASK 3"
      },
      {
        name: "frog",
        task: "TASK 4"
      },
      {
        name: "spikey",
        task: "TASK 5"
      },
    ]
    this.benchmarks.push({
      name: this.customInputName,
      inputs: []
    })
    this.enquiryIfBenchmarkIsRunning()
  }
}