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
                <mdb-tbl-head>
                  <tr>
                    <th
                    v-for="colHeader in data.columns"
                    :key="colHeader.label"
                    @mouseenter="setHovered(colHeader.field)"
                    @mouseleave="unsetHovered(colHeader.field)"
                    @click="sortRowsByIndex(colHeader.field)"
                    :style=hovered_headers[colHeader.field]>
                      {{colHeader.label}}  
                        <mdb-icon icon="sort" fas size="sm"
                          :style=hovered_sorts[colHeader.field]></mdb-icon></th>
                  </tr>
                </mdb-tbl-head>
                <mdb-tbl-body>
                  <tr v-for="(row, index) in data.rows" :key="index">
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
import { mdbRow, mdbCol, mdbCard, mdbView, mdbCardBody, mdbTbl, mdbTblHead, mdbTblBody, mdbScrollbar, mdbIcon } from 'mdbvue'
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
    mdbIcon
  },
  data () {
    return {
      data: {
        columns: [],
        rows: [],
      },
      hovered_sorts: [],
      hovered_headers: [],
      headers_sorted: []
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
          for (let i = 0; i < data.columns.length; i++) {
            hovered_sorts[data.columns[i].field] = "color: #ef6c00;"
            hovered_headers[data.columns[i].field] = "background-color: #f9a825"
            headers_sorted[data.columns[i].field] = "none"
          }
          this.data = data
          this.hovered_sorts = hovered_sorts
          this.hovered_headers = hovered_headers
        }.bind(this))
    },
    setHovered(index) {
      Vue.set(this.hovered_sorts, index, 'color: #e65100')
      Vue.set(this.hovered_headers, index, 'background-color: #f57f17')
    },
    unsetHovered(index) {
      Vue.set(this.hovered_sorts, index, 'color: #ef6c00;')
      Vue.set(this.hovered_headers, index, 'background-color: #f9a825')
    },
    sortRowsByIndex(index) {
      if (this.headers_sorted[index] != "asc") {
        this.data.rows.sort((a, b) => a[index] > b[index])
        Vue.set(this.headers_sorted, index, "asc")
      } else {
        this.data.rows.sort((a, b) => a[index] <= b[index])
        Vue.set(this.headers_sorted, index, "desc")
      }
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
  color: #fbd485
}
</style>
