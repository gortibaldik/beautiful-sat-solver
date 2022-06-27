import {
  mdbRow,
  mdbCol,
  mdbCard,
  mdbView,
  mdbCardBody,
  mdbTbl,
  mdbTblHead,
  mdbTblBody,
  mdbScrollbar,
  mdbIcon,
  mdbHorizontalBarChart
} from 'mdbvue'
import Vue from 'vue'

export default {
  name: 'Results',
  components: {
    mdbRow,
    mdbCol,
    mdbCard,
    mdbView,
    mdbCardBody,
    mdbTbl,
    mdbTblHead,
    mdbTblBody,
    mdbScrollbar,
    mdbIcon,
    mdbHorizontalBarChart
  },
  data () {
    return {
      data: {
        columns: [],
        rows: [],
      },
      filtered_rows: [],
      hovered_sorts: [],
      hovered_headers: [],
      hovered_filters: [],
      headers_sorted: [],
      uniques: [],
      selected_values: [],
      checked_rows: [],
      all_checked: false,
      unhovered_style: "background-color: #f9a825",
      button_unhovered_style: "background-color: #f9b74c",
      hovered_style: 'background-color: #f57f17',
      select_all_style: "background-color: #f9b74c",
      unhovered_compute_graph_style: "background-color: #1452b6",
      hovered_compute_graph_style: "background-color: #5595fb",
      compute_graph_style: "background-color: #1452b6",
      showBarChart: false,
      barChartData: {
        labels: [],
        datasets: [{
          label: '',
          data: [12, 19, 3, 5, 2, 3],
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
        'rgba(75, 192, 192, 0.2)'
      ],
      chartBorderColors: [
        'rgba(255,99,132,1)',
        'rgba(75, 192, 192, 1)'
      ],
      calculatedTableHeight: 0,
    }
  },
  created() {
    this.fetchBenchmarkResults()
  },
  methods: {
    fetchBenchmarkResults() {
      fetch("http://localhost:5000/results")
        .then(response => response.json())
        .then(function(data) {
          let hovered_sorts = {}
          let hovered_headers = {}
          let headers_sorted = {}
          let hovered_filters = {}
          let uniques = []
          let selected_values = {}
          let filtered_rows = []
          for (let i = 0; i < data.columns.length; i++) {
            hovered_sorts[data.columns[i].field] = "color: #e65100;"
            hovered_headers[data.columns[i].field] = this.unhovered_style
            hovered_filters[data.columns[i].field] = this.unhovered_style
            headers_sorted[data.columns[i].field] = "none"
            selected_values[data.columns[i].field] = "Show all"

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
                uniques[j].add(data.rows[i][data.columns[j].field])
              }
            }
            data.rows[i].checked = "is_unchecked"
            data.rows[i].originalIndex = i
            filtered_rows.push(data.rows[i])
          }
          this.data = data
          this.hovered_sorts = hovered_sorts
          this.hovered_headers = hovered_headers
          this.hovered_filters = hovered_filters
          this.uniques = uniques
          this.selected_values = selected_values
          this.filtered_rows = filtered_rows
          this.calculateTableHeight()
        }.bind(this))
    },
    setHovered(array, index) {
      Vue.set(array, index, this.hovered_style)
    },
    unsetHovered(array, index) {
      Vue.set(array, index, this.unhovered_style)
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
      for (let i = 0; i < this.filtered_rows.length; i++) {
        this.data.rows[this.filtered_rows[i].originalIndex].checked = this.filtered_rows[i].checked
      }
      for (let i = 0; i < this.data.rows.length; i++) {
        let equal_on_everything = true
        for (let j = 0; j < this.data.columns.length; j++) {
          if (this.selected_values[this.data.columns[j].field] != "Show all" && this.data.rows[i][this.data.columns[j].field] != this.selected_values[this.data.columns[j].field]) {
            equal_on_everything = false
            break
          }
        }
        if (equal_on_everything) {
          filtered_rows.push(this.data.rows[i])
        } else {
          this.data.rows[i].checked = "is_unchecked"
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
          newValue.checked = "is_unchecked"
        } else {
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
      if (this.all_checked) {
        this.checkAllImpl("is_unchecked")
        this.all_checked = false
      } else {
        this.checkAllImpl("is_checked")
        this.all_checked = true
      }
    },
    toggleGraphCreation() {
      let barChartData = {
        labels: [],
        datasets: []
      }
      for (let j = 0; j < this.data.columns.length; j++) {
        if (! this.data.columns[j].categorized) {
          barChartData.datasets.push({
            label: this.data.columns[j].label,
            data: [],
            backgroundColor: [],
            borderColor: [],
            borderWidth: 1
          })
        }
      }
      let checked = []
      for (let i = 0; i < this.filtered_rows.length; i++) {
        if (this.filtered_rows[i].checked == "is_checked") {
          checked.push(this.filtered_rows[i])
        }
      }
      if (checked.length === 0) {
        return
      }
      for (let i = 0; i < checked.length; i++) {
        barChartData.labels.push(`${checked[i]["algo"]} ${checked[i]["benchmark"]}`)
        let k = 0
        for (let j = 0; j < this.data.columns.length; j++) {
          if (! this.data.columns[j].categorized) {
            barChartData.datasets[k].data.push(Math.floor(checked[i][this.data.columns[j].field]))
            barChartData.datasets[k].backgroundColor.push(this.chartColors[k])
            barChartData.datasets[k].borderColor.push(this.chartBorderColors[k])

            k++
          }
        }
      }
      this.barChartData = barChartData
      this.showBarChart = true
      this.barChartHeight = 80 + checked.length * 50
      console.log(this.barChartHeight)
    },
    getViewportHeight() {
      const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0)
      return vh
    },
    calculateTableHeightInPx() {
      return 130 + this.filtered_rows.length * 70
    },
    calculateTableHeight() {
      let tblHeightInPx = this.calculateTableHeightInPx()
      if (tblHeightInPx < (0.7 * this.getViewportHeight())) {
        this.calculatedTableHeight = `${tblHeightInPx}px`
      } else {
        this.calculatedTableHeight = "70vh"
      }
      console.log(this.calculatedTableHeight)
    }
  }
}