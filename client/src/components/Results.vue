<template>
  <section id="tables">
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
          <mdb-view class="gradient-card-header blue darken-2">
            <h4 class="h4-responsive text-white">Results of Past Benchmark Runs</h4>
          </mdb-view>
          <mdb-card-body>
            <mdb-scrollbar height="70vh" class="border rounded-lg">
              <mdb-tbl style="background-color: white;">
                <mdb-tbl-head class="sticky-top z-depth-2">
                  <tr>
                    <th
                    v-for="colHeader in data.columns"
                    :key="colHeader.label"
                    @mouseenter="setHovered(hovered_headers, colHeader.field)"
                    @mouseleave="unsetHovered(hovered_headers, colHeader.field)"
                    @click="sortRowsByIndex(colHeader.field)"
                    :style="`${hovered_headers[colHeader.field]}; padding-top: 0.75rem; padding-bottom: 0rem`"
                    class="h5 text-monospace">
                    <ul class="list-inline">
                      <li class="list-inline-item">
                        {{colHeader.label}}   
                      </li>
                      <li class="list-inline-item" style="margin-left: 0.25rem">
                        <mdb-icon icon="sort" fas size="sm"
                          :style=hovered_sorts[colHeader.field]></mdb-icon>
                      </li>
                    </ul>
                    </th>
                    <th :style="`${unhovered_style}; padding-top: 0.75rem; padding-bottom: 0rem`"
                      class="h5 text-monospace">
                      <ul class="list-inline">
                        <li class="list-inline-item">
                          Select for Graph
                        </li>
                      </ul>
                    </th>
                  </tr>
                  <tr>
                    <th v-for="(colHeader, index) in data.columns"
                      :key="index"
                      :style="`${unhovered_style}; padding: 0.25rem`">
                      <select
                        v-if="uniques[index] != null"
                        class="browser-default custom-select h5-responsive text-monospace"
                        v-model="selected_values[colHeader.field]"
                        v-on:change="filterRows()"
                        :style="hovered_filters[colHeader.field]"
                        @mouseenter="uniques[index] != null ? setHovered(hovered_filters, colHeader.field) : () => {}"
                        @mouseleave="unsetHovered(hovered_filters, colHeader.field)">
                        <option
                          v-for="(val, indexUniques) in uniques[index]"
                          :key="indexUniques"
                          class="text-monospace">{{val}}</option>
                      </select>
                    </th>
                    <th :style="`${select_all_style}; padding: 0.25rem; padding-bottom: 0.75rem; padding-left: 0.75rem; color: #455a64`"
                      class="h5 text-monospace"
                      @mouseenter="select_all_style=hovered_style"
                      @mouseleave="select_all_style=button_unhovered_style"
                      @click="checkAll()">
                      <ul class="list-inline" style="margin-bottom: 0;">
                        <li class="list-inline-item">
                          {{all_checked ? 'Unselect All' : 'Select All'}}
                        </li>
                      </ul>
                    </th>
                  </tr>
                </mdb-tbl-head>
                <mdb-tbl-body>
                  <tr v-for="(row, index) in filtered_rows" :key="index">
                    <td v-for="(colHeader, indexC) in data.columns" :key="indexC" class="text-monospace h6" style="color: #455a64;">{{row[colHeader.field]}}</td>
                    <td>
                      <div class="input_wrapper" style="scale: 0.75">
                        <input type="checkbox" class="switch_4" @change="checkCheckbox(index)" :checked="checked_rows[index] === 'is_checked'">
                      </div>
                    </td>

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
      checked_rows: [],
      all_checked: false,
      unhovered_style: "background-color: #f9a825",
      button_unhovered_style: "background-color: #f9b74c",
      hovered_style: 'background-color: #f57f17',
      select_all_style: "background-color: #f9b74c",
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
          let checked_rows = []
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
            checked_rows.push(false)
          }
          this.data = data
          this.hovered_sorts = hovered_sorts
          this.hovered_headers = hovered_headers
          this.hovered_filters = hovered_filters
          this.uniques = uniques
          this.selected_values = selected_values
          this.filtered_rows = filtered_rows
          this.checked_rows = checked_rows
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
      this.checked_rows = Array(this.filtered_rows.length).fill("is_unchecked")
    },
    filterRows() {
      let filtered_rows = []
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
        }
      }
      this.filtered_rows = filtered_rows
      this.checked_rows = Array(this.filtered_rows.length).fill("is_unchecked")
    },
    checkCheckbox(index) {
      let oldValue = this.checked_rows[index]
      let newValue = ""
      if (oldValue === "is_checked") {
        newValue = "is_unchecked"
      } else {
        newValue = "is_checked"
      }
      Vue.set(this.checked_rows, index, newValue)
    },
    checkAll() {
      if (this.all_checked) {
        this.checked_rows = Array(this.filtered_rows.length).fill("is_unchecked")
        this.all_checked = false
      } else {
        this.checked_rows = Array(this.filtered_rows.length).fill("is_checked")
        this.all_checked = true
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
  margin-top: -50px;
  border-radius: 5px;
  margin-bottom: 10px;
}
.card.card-cascade h3,
.card.card-cascade h4 {
  margin-bottom: 0;
}
.card {
  background-color: transparent;
}

/* CSS styles for checkboxes: https://www.sliderrevolution.com/resources/css-checkbox/
- author: thelaazyguy
-  
 */
.input_wrapper{
  width: 80px;
  height: 40px;
  position: relative;
  cursor: pointer;
}

.input_wrapper input[type="checkbox"]{
  width: 80px;
  height: 40px;
  cursor: pointer;
  -webkit-appearance: none;
     -moz-appearance: none;
          appearance: none;
  background: #315e7f;
  border-radius: 2px;
  position: relative;
  outline: 0;
  -webkit-transition: all .2s;
  transition: all .2s;
}

.input_wrapper input[type="checkbox"]:after{
  position: absolute;
  content: "";
  top: 3px;
  left: 3px;
  width: 34px;
  height: 34px;
  background: #dfeaec;
  z-index: 2;
  border-radius: 2px;
  -webkit-transition: all .35s;
  transition: all .35s;
}

.input_wrapper .is_checked{
  width: 18px;
  left: 18%;
  -webkit-transform: translateX(190%) translateY(-30%) scale(0);
          transform: translateX(190%) translateY(-30%) scale(0);
}

.input_wrapper .is_unchecked{
  width: 15px;
  right: 10%;
  -webkit-transform: translateX(0) translateY(-30%) scale(1);
          transform: translateX(0) translateY(-30%) scale(1);
}

/* Checked State */
.input_wrapper input[type="checkbox"]:checked{
  background: #23da87;
}

.input_wrapper input[type="checkbox"]:checked:after{
  left: calc(100% - 37px);
}

.input_wrapper input[type="checkbox"]:checked + .is_checked{
  -webkit-transform: translateX(0) translateY(-30%) scale(1);
          transform: translateX(0) translateY(-30%) scale(1);
}

.input_wrapper input[type="checkbox"]:checked ~ .is_unchecked{
  -webkit-transform: translateX(-190%) translateY(-30%) scale(0);
          transform: translateX(-190%) translateY(-30%) scale(0);
}
</style>
