library(dplyr)
library(readr)
library(stringr)
library(bupaR)
library(tidyr)
library(xesreadR)
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

args = commandArgs(trailingOnly=TRUE)
epsilon <- args[1]
sequence_length <- args[2]
sequence_threshold <- args[3]
csv_path <- args[4]
outPath <- args[5]

log_private <- read_csv(url(paste0("http://localhost:1234/traces?epsilon=", epsilon, "&sequence_threshold=", sequence_threshold, "&sequence_length=", sequence_length )),
					   col_types = cols(
						 Sequence = col_character(),
						 Count = col_integer()
					   ))%>%
     convert_traces(read_csv(paste0(csv_path,"activities.csv"), col_types = cols(
                                                     Activity = col_character(),
                                                     Id = col_integer()
                                                   ))) %>%
     eventlog(case_id = "case", activity_id = "Activity", activity_instance_id = "act_id", 
              lifecycle_id = "lifecyle", timestamp = "timestamp", resource_id = "resource")
  
write_xes(log_private, outPath)
