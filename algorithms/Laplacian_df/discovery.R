library(dplyr)
library(readr)
library(stringr)
library(bupaR)
library(xesreadR)
library(tidyr)
source("prom_utils.R")


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

args = commandArgs(trailingOnly=TRUE)
epsilon <- args[1]
outPath <- args[2]

dfg_private <- read_csv(url(paste0("http://localhost:1234/events?epsilon=", epsilon))) %>% 
    convert_precedence()
  
  #write_csv(dfg_private, paste("lapl_rtf_0_",epsilon,x,".csv"))
write_prom_dfg(dfg_private, outPath)