<template>
  <section id="tables">
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5">
          <mdb-view class="gradient-card-header blue darken-2">
            <h4 class="h4-responsive text-white">Results of Past Benchmark Runs</h4>
          </mdb-view>
          <mdb-card-body>
            <mdb-scrollbar height="70vh">
              <mdb-tbl>
                <mdb-tbl-head class="sticky-top z-depth-3">
                  <tr>
                    <th
                    v-for="colHeader in data.columns"
                    :key="colHeader.label"
                    @mouseenter="setHovered(hovered_headers, colHeader.field)"
                    @mouseleave="unsetHovered(hovered_headers, colHeader.field)"
                    @click="sortRowsByIndex(colHeader.field)"
                    :style=hovered_headers[colHeader.field]>
                      {{colHeader.label}}  
                        <mdb-icon icon="sort" fas size="sm"
                          :style=hovered_sorts[colHeader.field]></mdb-icon></th>
                  </tr>
                  <tr>
                    <th v-for="(colHeader, index) in data.columns" :key="index"
                      @mouseenter="uniques[index] != null ? setHovered(hovered_filters, colHeader.field) : () => {}"
                      @mouseleave="unsetHovered(hovered_filters, colHeader.field)"
                      :style=hovered_filters[colHeader.field]>
                      <select v-if="uniques[index] != null" class="browser-default custom-select" v-model="selected_values[colHeader.field]" v-on:change="filterRows(colHeader.field, selected_values[colHeader.field])">
                        <option v-for="(val, indexUniques) in uniques[index]" :key="indexUniques">{{val}}</option>
                      </select>
                    </th>
                  </tr>
                </mdb-tbl-head>
                <mdb-tbl-body>
                  <tr v-for="(row, index) in filtered_rows" :key="index">
                    <td v-for="(colHeader, indexC) in data.columns" :key="indexC">{{row[colHeader.field]}}</td>
                  </tr>
                </mdb-tbl-body>
              </mdb-tbl>
            </mdb-scrollbar>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
  </section>
</template>

<script>
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
  mdbIcon
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
      unhovered_style: "background-color: #f9a825",
      hovered_style: 'background-color: #f57f17'
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
            filtered_rows.push(data.rows[i])
          }
          this.data = data
          this.hovered_sorts = hovered_sorts
          this.hovered_headers = hovered_headers
          this.hovered_filters = hovered_filters
          this.uniques = uniques
          this.selected_values = selected_values
          this.filtered_rows = filtered_rows
          console.log(filtered_rows)
          console.log(uniques)
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
    filterRows(index, value) {
      let filtered_rows = []
      for (let i = 0; i < this.data.rows.length; i++) {
        if (this.data.rows[i][index] === value) {
          filtered_rows.push(this.data.rows[i])
        }
      }
      this.filtered_rows = filtered_rows
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.card.card-cascade .view.gradient-card-header {
  padding: 1rem 1rem;
  text-align: center;
}
.card.card-cascade h3,
.card.card-cascade h4 {
  margin-bottom: 0;
}
</style>
