<template>
  <section id="tables">
    <mdb-card class="mb-4">
      <mdb-card-body class="title-class d-sm-flex justify-content-between">
        <h4 class="mb-sm-0 pt-2">
          Results of Past Benchmark Runs
        </h4>
      </mdb-card-body>
    </mdb-card>
    <mdb-row class="results-row">
      <mdb-card cascade narrow class="custom-margin-top border border-0 border-dark">
        <mdb-card-body class="results-table">
          <mdb-scrollbar :style="`height: ${calculatedTableHeight};`" class="border rounded-lg">
            <mdb-tbl style="background-color: white;" autoWidth>
              <mdb-tbl-head class="sticky-top z-depth-2">
                <tr>
                  <th
                  v-for="colHeader in data.columns"
                  :key="colHeader.label"
                  @mouseenter="setHovered(hovered_headers, colHeader.label)"
                  @mouseleave="unsetHovered(hovered_headers, colHeader.label)"
                  @click="sortRowsByIndex(colHeader.label)"
                  :style="`${hovered_headers[colHeader.label]}; padding-top: 0.75rem; padding-bottom: 0rem`"
                  :class="`h6 text-monospace ${textWrapClass}`">
                  <ul class="list-inline">
                    <li class="list-inline-item">
                      {{getViewportWidth() >= 1200 ? colHeader.label : colHeader.field}}   
                    </li>
                    <li class="list-inline-item" style="margin-left: 0.25rem">
                      <mdb-icon icon="sort" fas size="sm"
                        :style=hovered_sorts[colHeader.label]></mdb-icon>
                    </li>
                  </ul>
                  </th>
                  <th :style="`${unhovered_style}`"/>
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
                      v-model="selected_values[colHeader.label]"
                      v-on:change="filterRows()"
                      :style="hovered_filters[colHeader.label]"
                      @mouseenter="uniques[index] != null ? setHovered(hovered_filters, colHeader.label) : () => {}"
                      @mouseleave="unsetHovered(hovered_filters, colHeader.label)">
                      <option
                        v-for="(val, indexUniques) in uniques[index]"
                        :key="indexUniques"
                        class="text-monospace">{{val}}</option>
                    </select>
                  </th>
                  <th :style="`${unhovered_style}`"/>
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
                  <td
                    v-for="(colHeader, indexC) in data.columns"
                    :key="indexC"
                    class="text-monospace"
                    :style="`color: #455a64; ${colHeader.can_be_pressed ? show_log_file_styles[index] : ''}`"
                    @click="colHeader.can_be_pressed ? showLogFile(index) : () => {}"
                    @mouseenter="colHeader.can_be_pressed ? setShowLogFileHovered(index) : () => {}"
                    @mouseleave="colHeader.can_be_pressed ? unsetShowLogFileHovered(index) : () => {}"
                  >{{ colHeader.can_be_pressed
                        ? "Show"
                        : isFloat(row[colHeader.label])
                          ? row[colHeader.label].toLocaleString("en-US", { maximumFractionDigits: 2, minimumFractionDigits: 2 })
                          : row[colHeader.label]}}</td>
                  <td
                    class="text-monospace"
                    :style="`color: #455a64; ${delete_button_styles[index]}`"
                    @click="deleteLogFile(index)"
                    @mouseenter="setDeleteHovered(index)"
                    @mouseleave="unsetDeleteHovered(index)"
                  >
                    Delete
                  </td>
                  <td>
                    <div class="input_wrapper" style="scale: 0.75">
                      <input type="checkbox" class="switch_4" @change="checkCheckbox(index)" :checked="row.checked === 'is_checked'">
                    </div>
                  </td>
                  <mdb-modal size="fluid" :show="displayed_modals[index]" @close="closeModal(index)" scrollable>
                    <mdb-modal-header>
                      <mdb-modal-title>Algorithm result</mdb-modal-title>
                    </mdb-modal-header>
                    <mdb-modal-body v-html="modal_messages[index]">
                    </mdb-modal-body>
                    <mdb-modal-footer>
                      <mdb-btn color="secondary" @click.native="closeModal(index)">Close</mdb-btn>
                    </mdb-modal-footer>
                  </mdb-modal>
                </tr>
              </mdb-tbl-body>
            </mdb-tbl>
          </mdb-scrollbar>
        </mdb-card-body>
      </mdb-card>
    </mdb-row>
    <mdb-row>
      <mdb-col md="12">
        <mdb-card cascade narrow class="mt-5 border border-0 border-dark">
          <mdb-view class="gradient-card-header blue darken-2" style="padding: 0;">
            <ul class="list-inline" style="margin-bottom: 0px;">
              <li class="graph-li-class list-inline-item">
                <h4 class="h4-responsive text-white">Graph</h4>
              </li>
              <li :class="`header-button-style list-inline-item ${compute_graph_class}`"
                @mouseenter="compute_graph_class=hovered_compute_graph_class"
                @mouseleave="compute_graph_class=unhovered_compute_graph_class"
                @click="toggleGraphCreation()">
                <h4 class="h4-responsive text-white">Compute from Selected</h4>
              </li>
              <li :class="`header-button-style list-inline-item ${download_csv_class}`"
                @mouseenter="download_csv_class=hovered_download_csv_class"
                @mouseleave="download_csv_class=unhovered_download_csv_class"
                @click="downloadCsv()"
              >
                <h4 class="h4-responsive text-white">Download .csv</h4>
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