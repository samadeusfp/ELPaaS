library(tidyverse)
library(readr)
library(stringr)
library(bupaR)
library(xesreadR)
library(dplyr)
source("heuristic_miner.R")
source("prom_utils.R")
library(DiagrammeRsvg)


convert_precedence <- function(csv) {
  csv %>% 
    select(antecedent = Source,
           consequent = Target,
           n = Count) %>%     
    filter(n > 0) %>%
    filter(antecedent != "End", 
           consequent != "Start") # filter obvious nonsense
}

convert_traces <- function(csv, activity_lookup) {
  csv %>%
    mutate(variant = 1:n()) %>%
    mutate(Sequence = as.character(Sequence)) %>%
    #mutate(Sequence = sapply(str_split(as.character(Sequence), pattern = "<"), paste, collapse = ",")) %>%
    separate_rows(Sequence, sep = "<") %>%
    rename("Id" = Sequence) %>%
    mutate(Id = as.integer(Id)) %>%
    left_join(activity_lookup, by = c("Id" = "Id")) %>%
    group_by(variant) %>%
    slice(c(-1,-n())) %>% # remove artifical start/end
    do({
      count <- max(.$Count)
      length <- nrow(.)
      slice(., rep(1:n(), times=count)) %>%
        mutate(case = ceiling(row_number() / length))
    }) %>%
    ungroup() %>%
    mutate(act_id = 1:n(),
           case = paste0(variant,"-",case)) %>%
    mutate(timestamp = as.POSIXct(act_id, origin = "1970-01-01"),
           resource = "",
           lifecyle = "complete")
}

#
# Evaluation Directly-Follows Graph Variant & Heuristic Miner / Dependency Graph
#

lapply(c(1:10), function(x) {

  dep_threshold <- .9
  obs_threshold <- .05
  epsilon <- 0.01

  dfg_private <- read_csv(url(paste0("http://localhost:1234/events?epsilon=", epsilon))) %>% 
    convert_precedence()
  
  #write_csv(dfg_private, paste("lapl_rtf_0_",epsilon,x,".csv"))
  write_prom_dfg(dfg_private, paste0("lapl_rtf_0_0.01_",x,".dfg"))
  
  #dfg_private %>%
  #  filter(antecedent != "End", consequent != "Start") %>% 
  #  filter(n > obs_threshold * max(n)) %>%
  #  dependency_matrix() %>%
  #  filter(dep > dep_threshold) %>%
  #  dependency_graph(render = F) %>%
  #  export_graph(paste0("private",x, ".pdf"))
  
  #dfg_original <- read_csv(file = "log-precedence-matrix.csv")
  #dfg_original %>%
  #  filter(antecedent != "End", consequent != "Start") %>% 
  #  filter(n > obs_threshold * max(n)) %>%
  #  dependency_matrix() %>%
  #  filter(dep > dep_threshold) %>%
  #  dependency_graph(render = F) %>%
  #  export_graph(paste0("original",x, ".pdf"))
  
})

#
# Evaluation Trace Variants & Heuristic Miner / Dependency Graph
#

#~ lapply(c(1:10), function(x) {

#~   dep_threshold <- .9
#~   obs_threshold <- .05
#~   epsilon <- 0.01
#~   sequence_threshold <- 350
#~   sequence_length <- 15

#~   log_private <- read_csv(url(paste0("http://localhost:1234/traces?epsilon=", epsilon, "&sequence_threshold=", sequence_threshold, "&sequence_length=", sequence_length )),
#~                           col_types = cols(
#~                             Sequence = col_character(),
#~                             Count = col_integer()
#~                           )) %>%
#~     convert_traces(read_csv("sepsis_log-activities.csv", col_types = cols(
#~                                                     Activity = col_character(),
#~                                                     Id = col_integer()
#~                                                   ))) %>%
#~     eventlog(case_id = "case", activity_id = "Activity", activity_instance_id = "act_id", 
#~              lifecycle_id = "lifecyle", timestamp = "timestamp", resource_id = "resource")
  
#~   write_xes(log_private, paste0("lapl_sepsis_1_",epsilon,"_",x,".xes"))
  
#~   log_private %>%
#~     precedence_matrix() %>%
#~     filter(n > obs_threshold * max(n)) %>%
#~     dependency_matrix() %>%
#~     filter(dep > dep_threshold) %>%
#~     dependency_graph(render = F) %>%
#~     export_graph(paste0("variants-private",x, ".pdf"))
  
#~   log_original <- read_xes("log-original.xes")
#~   log_original %>%
#~     precedence_matrix() %>%
#~     filter(antecedent != "End", consequent != "Start") %>% 
#~     filter(n > obs_threshold * max(n)) %>%
#~     dependency_matrix() %>%
#~     filter(dep > dep_threshold) %>%
#~     dependency_graph(render = F) %>%
#~     export_graph(paste0("variants-original",x, ".pdf"))
  
#~   process_map(log_private)
#~	})

