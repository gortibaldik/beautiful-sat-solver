import {
  mdbRow,
  mdbCol,
  mdbCard,
  mdbView,
  mdbCardBody,
  mdbCardTitle,
  mdbTbl,
  mdbTblHead,
  mdbTblBody,
  mdbScrollbar,
  mdbIcon,
  mdbHorizontalBarChart,
  mdbLineChart,
  mdbBtn,
  mdbModal,
  mdbModalBody,
  mdbModalFooter,
  mdbModalHeader,
  mdbModalTitle,
} from 'mdbvue'
import Vue from 'vue'
import results_comm from '@/assets/js/results_communication'

export default {
  name: 'Results',
  title: 'SAT: Results',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbView,
    mdbCardBody,
    mdbCardTitle,
    mdbTbl,
    mdbTblHead,
    mdbTblBody,
    mdbScrollbar,
    mdbIcon,
    mdbHorizontalBarChart,
    mdbLineChart,
    mdbBtn,
    mdbModal,
    mdbModalBody,
    mdbModalFooter,
    mdbModalHeader,
    mdbModalTitle,
  },
  data () {
    return {
      data: {
        columns: [],
        rows: [],
      },
      filtered_rows: [],
      headers_sorted: [],
      uniques: [],
      selected_values: [],
      checked_rows: [],
      displayed_modals: [],
      modal_messages: [],
      all_checked: false,
      no_checked: 0,
      serverAddress: "",
      textWrapClass: "text-nowrap",
      showBarChart: false,
      barChartData: {
        labels: [],
        datasets: [{
          label: '',
          data: [],
          backgroundColor: [],
          borderColor: [],
          borderWidth: 1,
        }]
      },
      barChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            barPercentage: 1,
            gridLines: {
              display: true,
              color: "rgba(0, 0, 0, 0.1)"
            }
          }],
          yAxes: [{
            gridLines: {
              display: true,
              color: "rgba(0, 0, 0, 0.1)"
            }
          }]
        }
      },
      barChartHeight: 0,
      chartColors: [
        'rgba(255, 99, 132, 0.2)',
        'rgba(75, 192, 192, 0.2)',
        'rgba(26, 171, 38, 0.2)',
        'rgba(127, 16, 237, 0.2)',
      ],
      chartBorderColors: [
        'rgba(255,99,132,1)',
        'rgba(75, 192, 192, 1)',
        'rgba(9, 129, 19, 0.2)',
        'rgba(70, 30, 110, 0.2)',
      ],
      lineChartTimeData: {
        labels: [],
        datasets: [
          {
            label: "",
            backgroundColor: "",
            borderColor: "",
            borderWidth: 0,
            data: []
          }
        ]
      },
      lineChartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            gridLines: {
              display: true,
              color: "rgba(0, 0, 0, 0.1)"
            }
          }],
          yAxes: [{
            gridLines: {
              display: true,
              color: "rgba(0, 0, 0, 0.1)"
            }
          }]
        }
      },
      calculatedTableHeight: 0,
    }
  },
  created() {
    window.addEventListener('resize', this.onResize)
    this.onResize()
    this.serverAddress = process.env.VUE_APP_SERVER_ADDRESS
    this.initBenchmarkResults()
  },
  methods: {
    async initBenchmarkResults() {
      let data = await results_comm.fetchBenchmarkResults(this.serverAddress)
      let headers_sorted = {}
      let uniques = []
      let selected_values = {}
      let filtered_rows = []
      let displayed_modals = []
      let modal_messages = []
      for (let i = 0; i < data.columns.length; i++) {
        headers_sorted[data.columns[i].label] = "none"
        selected_values[data.columns[i].label] = "Show all"

        // each column has a special "categorized"
        // attribute which shows whether there should
        // be a filter for selecting one of the unique
        // values of rows in the column
        if (data.columns[i].categorized) {
          uniques.push(new Set())
          uniques[i].add("Show all")
        } else {
          uniques.push(null)
        }
      }
      for (let i = 0; i < data.rows.length; i++) {
        for (let j = 0; j < data.columns.length; j++) {
          if (data.columns[j].categorized) {
            uniques[j].add(data.rows[i][data.columns[j].label])
          }
        }
        data.rows[i].checked = "is_unchecked"
        data.rows[i].originalIndex = i
        filtered_rows.push(data.rows[i])

        displayed_modals.push(false)
        modal_messages.push(false)
      }
      this.data = data
      this.uniques = uniques
      this.selected_values = selected_values
      this.filtered_rows = filtered_rows
      this.displayed_modals = displayed_modals
      this.modal_messages = modal_messages
      this.calculateTableHeight()
    },
    canBePressedClass(colHeader) {
      if (colHeader.can_be_pressed) {
        return "can-be-pressed"
      } else {
        return ""
      }
    },
    tableDataContent(colHeader, row) {
      if (colHeader.can_be_pressed) {
        return "Show"
      }

      // each float displayed with only 2 decimals
      if (this.isFloat(row[colHeader.label])) {
        return row[colHeader.label].toLocaleString(
          "en-US",
          { 
            maximumFractionDigits: 2,
            minimumFractionDigits: 2 
          }
        )
      }

      return row[colHeader.label]
    },
    sortRowsByIndex(index) {
      if (this.headers_sorted[index] != "asc") {
        this.filtered_rows.sort((a, b) => a[index] > b[index])
        Vue.set(this.headers_sorted, index, "asc")
      } else {
        this.filtered_rows.sort((a, b) => a[index] <= b[index])
        Vue.set(this.headers_sorted, index, "desc")
      }
    },
    filterRows() {
      let filtered_rows = []
      this.no_checked = 0
      for (let i = 0; i < this.filtered_rows.length; i++) {
        this.data.rows[this.filtered_rows[i].originalIndex].checked = this.filtered_rows[i].checked
      }
      for (let i = 0; i < this.data.rows.length; i++) {
        let equal_on_everything = true
        for (let j = 0; j < this.data.columns.length; j++) {
          if (this.selected_values[this.data.columns[j].label] != "Show all" &&
              this.data.rows[i][this.data.columns[j].label] != this.selected_values[this.data.columns[j].label]) {
            equal_on_everything = false
            break
          }
        }
        if (equal_on_everything) {
          filtered_rows.push(this.data.rows[i])
          if (this.data.rows[i].checked == "is_checked") {
            this.no_checked++
          }
        }
      }
      this.filtered_rows = filtered_rows
      this.calculateTableHeight()
    },
    checkCheckbox(index, value=null) {
      let oldValue = this.filtered_rows[index]
      let newValue = { ...oldValue }
      if (value != null) {
        newValue.checked = value
      } else {
        if (oldValue.checked === "is_checked") {
          this.no_checked--
          newValue.checked = "is_unchecked"
        } else {
          this.no_checked++
          newValue.checked = "is_checked"
        }
      }
      Vue.set(this.filtered_rows, index, newValue)
    },
    checkAllImpl(value) {
      for (let i = 0; i < this.filtered_rows.length; i++) {
        this.checkCheckbox(i, value)
      } 
    },
    checkAll() {
      if (this.no_checked !== 0) {
        this.checkAllImpl("is_unchecked")
        this.no_checked = 0
      } else {
        this.checkAllImpl("is_checked")
        this.no_checked = this.filtered_rows.length
      }
    },
    cumulativeVisualizationCreation(checked) {
      let barChartData = {
        labels: [],
        datasets: []
      }
      for (let j = 0; j < this.data.columns.length; j++) {
        if (this.data.columns[j].plotted) {
          barChartData.datasets.push({
             // time/unit props etc. are examples of datasets
            label: this.data.columns[j].label,
            data: [],
            backgroundColor: [],
            borderColor: [],
            borderWidth: 1
          })
        }
      }
      for (let i = 0; i < checked.length; i++) {
        barChartData.labels.push(`${checked[i]["Algorithm"]} ${checked[i]["Benchmark"]}`)
        let k = 0
        for (let j = 0; j < this.data.columns.length; j++) {
          if (this.data.columns[j].plotted) {
            barChartData.datasets[k].data.push(checked[i][this.data.columns[j].label])
            barChartData.datasets[k].backgroundColor.push(this.chartColors[k])
            barChartData.datasets[k].borderColor.push(this.chartBorderColors[k])

            k++
          }
        }
      }
      this.barChartData = barChartData
      this.barChartHeight = 80 + checked.length * 50
    },
    visualizationCreation(checked, nameOfField) {
      let chartData = {
        labels: [],
        datasets: []
      }
      // datasets are sets of time results of algorithms
      // labels are names of benchmarks
      let datasetNamesSet = new Set();
      let labelsSet = new Set();
      for (let i = 0; i < checked.length; i++) {
        datasetNamesSet.add(checked[i]["Algorithm"])
        labelsSet.add(checked[i]["Benchmark"])
      }
      let datasetNames = Array.from(datasetNamesSet)
      let labelNames = Array.from(labelsSet)
      chartData.labels = labelNames
      for (let i = 0; i < datasetNames.length; i++) {
        chartData.datasets.push({
          label: datasetNames[i],
          data: [],
          backgroundColor: this.chartColors[i],
          borderColor: this.chartBorderColors[i],
          borderWidth: 1
        })
      }

      for (let dix = 0; dix < datasetNames.length; dix++) {
        for (let lnix = 0; lnix < labelNames.length; lnix++) {
          let data = undefined;
          for (let cix = 0; cix < checked.length; cix++) {
            if (checked[cix]["Algorithm"] == datasetNames[dix] &&
                checked[cix]["Benchmark"] == labelNames[lnix]) {
              data = checked[cix][nameOfField]
            }
          }
          chartData.datasets[dix].data.push(data)
        }
      }
      return chartData
    },
    getCheckedRows() {
      let checked = []
      for (let i = 0; i < this.filtered_rows.length; i++) {
        if (this.filtered_rows[i].checked == "is_checked") {
          checked.push(this.filtered_rows[i])
        }
      }
      return checked
    },
    toggleGraphCreation() {
      let checked = this.getCheckedRows()
      if (checked.length === 0) {
        return
      }
      this.cumulativeVisualizationCreation(checked)
      this.visualizations = []
      for (let i = 0; i < this.data.columns.length; i++) {
        if (this.data.columns[i].plotted) {
          let d = this.visualizationCreation(checked, this.data.columns[i].label)
          this.visualizations.push({
            title: this.data.columns[i].label,
            data: d
          })
        }
      }
      this.showBarChart = true
    },
    downloadCsv() {
      // write headers
      let csvContent = ""
      for (let j = 0; j < this.data.columns.length; j++) {
        csvContent += this.data.columns[j].label
        if (j < this.data.columns.length - 1) {
          csvContent += ", "
        } else {
          csvContent += "\n"
        }
      }

      // select checked rows
      let checked = this.getCheckedRows()
      if (checked.length == 0) {
        return
      }

      // write data
      for (let i = 0; i < checked.length; i++) {
        for (let j = 0; j < this.data.columns.length; j++) {
          let content = String(checked[i][this.data.columns[j].label])
          if (content.includes(",")) {
            content = `"${content}"`
          }
          csvContent += content
          if (j < this.data.columns.length - 1) {
            csvContent += ", "
          } else {
            csvContent += "\n"
          }
        }
      }

      // download action
      let hiddenElement = document.createElement('a');  
      hiddenElement.href = 'data:text/csv;charset=utf-8,' + encodeURI(csvContent);  
      hiddenElement.target = '_blank';  
        
      //provide the name for the CSV file to be downloaded  
      hiddenElement.download = 'benchmark_data.csv';  
      hiddenElement.click();  
    },
    getViewportHeight() {
      const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
      return vh
    },
    getViewportWidth() {
      return Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    },
    onResize() {
      if (this.getViewportWidth() < 1200) {
        this.textWrapClass = ""
      } else {
        this.textWrapClass = "text-nowrap"
      }
    },
    isFloat(n) {
      return n === +n && n !== (n|0);
    },
    calculateTableHeightInPx() {
      return 200 + this.filtered_rows.length * 70
    },
    calculateTableHeight() {
      let tblHeightInPx = this.calculateTableHeightInPx()
      if (tblHeightInPx < (0.7 * this.getViewportHeight())) {
        this.calculatedTableHeight = `${tblHeightInPx}px`
      } else {
        this.calculatedTableHeight = "70vh"
      }
    },
    closeModal(index) {
      Vue.set(this.displayed_modals, index, false)
    },
    async showLogFile(index) {
      let data = await results_comm.fetchLogFile(
        this.serverAddress,
        this.filtered_rows[index]["Log File"]
      )
      if (data["result"] === "failure") {
        return
      }
      Vue.set(this.displayed_modals, index, true)
      Vue.set(this.modal_messages, index, data["result"])
    },
    removeLogFileFromDataRows(index) {
      let log_file = this.filtered_rows[index]["Log File"]
      let theIndex = -1
      for (let i = 0; i < this.data.rows.length; i++) {
        if (this.data.rows[i]["Log File"] === log_file) {
          theIndex = i
        } else if (theIndex != -1) {
          this.data.rows[i].originalIndex = i - 1
        }
      }
      this.data.rows.splice(theIndex, 1)
    },
    async deleteLogFile(index) {
      let data = await results_comm.fetchDeleteLogFile(
        this.serverAddress,
        this.filtered_rows[index]["Log File"]
      )
      if (data["result"] === "failure") {
        return
      }
      this.removeLogFileFromDataRows(index)
      this.filtered_rows.splice(index, 1)
    },
  }
}