library(dplyr)
library(bupaR)
library(readr)
library(tidyr)

# utility functions from bupaR
case_id_ <- function(eventlog) sym(case_id(eventlog))
activity_id_ <- function(eventlog) sym(activity_id(eventlog))
activity_instance_id_ <- function(eventlog) sym(activity_instance_id(eventlog))
resource_id_ <- function(eventlog) sym(resource_id(eventlog))
timestamp_ <- function(eventlog) sym(timestamp(eventlog))
lifecycle_id_ <- function(eventlog) sym(lifecycle_id(eventlog))

abcify_log <- function(eventlog) {
  levels(eventlog[[activity_id(eventlog)]]) <- LETTERS[1:length(unique(eventlog[[activity_id(eventlog)]]))]
}

write_activities_pinq <- function(eventlog, path = "activity.csv") {
  
  activities <- eventlog %>%
    data.frame() %>%
    select("Activity" = activity_id(eventlog)) %>% 
    distinct() %>% 
    mutate_all(as.character) %>%
    rbind(data.frame(Activity = c("Start","End"))) %>%
    arrange(Activity) %>%
    mutate(Id = 1:n())
    
  write_csv(activities, path)
  
  activities
}

write_precedence_pinq <- function(eventlog, path = "precedence.csv") {
  
  temp <- eventlog %>%
    group_by(!!case_id_(eventlog), !!activity_id_(eventlog), !!activity_instance_id_(eventlog)) %>%
    summarize(ts = min(!!timestamp_(eventlog)), min_order = min(.order))  %>%
    group_by(!!case_id_(eventlog)) %>%
    arrange(ts, min_order) %>%
    mutate(antecedent = as.character(!!activity_id_(eventlog)),
  	  	   consequent = lead(as.character(!!activity_id_(eventlog)), default = "End"))
  
  precedence_log <- temp %>%
    slice(1:1) %>%
  	mutate(consequent = antecedent,
  	       antecedent = "Start") %>%
  	bind_rows(temp) %>%
    ungroup() %>% 
    mutate(Relation = paste0(antecedent,",",consequent)) %>%
    ungroup() %>%
    select(Source = antecedent,
           Target = consequent,
           Relation,
           Time = ts) #TODO add some other attributes
  
  write_csv(precedence_log, path)

  precedence_log
}

write_precedence_percase_pinq <- function(eventlog, path = "precedence-percase.csv") {
  
  #
  # Emulates a 3D matrix representation of the directly-follow relations in which each matrix slice is a case.
  #

  precedence_log <- eventlog %>%
    group_by(!!case_id_(eventlog), !!activity_id_(eventlog), !!activity_instance_id_(eventlog)) %>%
    summarize(ts = min(!!timestamp_(eventlog)), min_order = min(.order))  %>%
    group_by(!!case_id_(eventlog)) %>%
    arrange(ts, min_order) %>%
    mutate(antecedent = as.character(!!activity_id_(eventlog)),
  	  	   consequent = lead(as.character(!!activity_id_(eventlog)), default = "End")) %>%
    mutate(relation = paste0(antecedent,",",consequent)) %>%
    spread(relation, relation) %>%
    select(-(!!activity_id(eventlog)), -(!!activity_instance_id(eventlog)), -ts, -min_order, -antecedent, -consequent) %>%
    summarise_all(funs(sum(!is.na(.))))
  
  write_csv(precedence_log, path)
  
  precedence_log
}

write_sequences_pinq <- function(eventlog, activity_lookup, path = "sequences.csv") {
  
  startId <- activity_lookup %>% filter(Activity == "Start") %>% pull(Id)
  endId <- activity_lookup %>% filter(Activity == "End") %>% pull(Id)
  
  precedence_log <- eventlog %>%
    group_by(!!case_id_(eventlog), !!activity_id_(eventlog), !!activity_instance_id_(eventlog)) %>%
    summarize(ts = min(!!timestamp_(eventlog)), min_order = min(.order))  %>%
    group_by(!!case_id_(eventlog)) %>%
    arrange(ts, min_order) %>%
    mutate_at(.vars = activity_id(eventlog), .funs = as.character) %>%
    left_join(activity_lookup, by = setNames("Activity", activity_id(eventlog))) %>%
    summarise(Sequence = paste0(startId, "<", paste0(Id, collapse = "<"), "<", endId), MinTimestamp = min(ts), MaxTimestamp = max(ts)) %>% # TODO add other attributes
    select(-(!!case_id(eventlog)))

  write_csv(precedence_log, path)  
  
  precedence_log
}

#log <- traffic_fines
args = commandArgs(trailingOnly=TRUE)
log <- read_xes(args[1])
out_dir <-args[2]

activity_lookup <- write_activities_pinq(log, paste0(out_dir,"/activities.csv"))
#write_xes(log, paste0(out_dir,"/original.xes"))
write_precedence_pinq(log, paste0(out_dir,"/precedence.csv"))
write_precedence_percase_pinq(log, paste0(out_dir,"/precedence-percase.csv"))
#write_csv(precedence_matrix(log), paste0(out_dir,"/precedence-matrix.csv"))
write_sequences_pinq(log, activity_lookup, paste0(out_dir,"/log-sequences.csv"))
quit()
