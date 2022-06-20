<template>
  <section id="tables">
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
          <mdb-view class="gradient-card-header blue darken-2">
            <h4 class="h4-responsive text-white">Results of Past Benchmark Runs</h4>
          </mdb-view>
          <mdb-card-body>
            <mdb-scrollbar :style="`height: ${calculatedTableHeight};`" class="border rounded-lg">
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
                    class="h6 text-monospace">
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
                      class="h6 text-monospace">
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
                        class="browser-default custom-select h6-responsive text-monospace"
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
                      class="h6 text-monospace"
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
                        <input type="checkbox" class="switch_4" @change="checkCheckbox(index)" :checked="row.checked === 'is_checked'">
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
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
          <mdb-view class="gradient-card-header blue darken-2" style="padding: 0;">
            <ul class="list-inline" style="margin-bottom: 0px;">
              <li class="list-inline-item" style="padding-top:13px; height: 50px;">
                <h4 class="h4-responsive text-white">Graph</h4>
              </li>
              <li class="list-inline-item"
                :style="`float: right; ${compute_graph_style}; padding-top:13px; height: 50px; padding-right: 5px; padding-left: 5px`"
                @mouseenter="compute_graph_style=hovered_compute_graph_style"
                @mouseleave="compute_graph_style=unhovered_compute_graph_style"
                @click="toggleGraphCreation()">
                <h4 class="h4-responsive text-white">Compute from Selected</h4>
              </li>
            </ul>
          </mdb-view>
          <mdb-card-body>
            <mdb-horizontal-bar-chart
              :data="barChartData"
              :options="barChartOptions"
              :style="`display: ${showBarChart ? '' : 'none'}; height: ${barChartHeight}px`">
            </mdb-horizontal-bar-chart>
          </mdb-card-body>
        </mdb-card>
      </mdb-col>
    </mdb-row>
  </section>
</template>

<script src="@/assets/js/results.js" />
<style scoped src="@/assets/styles/results.css" />