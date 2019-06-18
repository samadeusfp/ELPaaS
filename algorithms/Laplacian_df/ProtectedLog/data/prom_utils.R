write_prom_dfg <- function(precedence_matrix, path) {
  conn<-file(path, open = "wt")
  
  # avoid joining issues with factors
  precedence_matrix <- precedence_matrix %>%
    mutate(antecedent = as.character(antecedent),
           consequent = as.character(consequent))
  
  activities <- data.frame(act = union(precedence_matrix$antecedent, 
                                       precedence_matrix$consequent), 
                           stringsAsFactors = FALSE) %>%
    mutate(id = 0:(n()-1))
  
  # Number of activities 
  writeLines(as.character(nrow(activities)), conn)
  writeLines(activities$act, conn)

  start_acts <- precedence_matrix %>%
      anti_join(precedence_matrix, by = c("antecedent" = "consequent")) %>%
      group_by(antecedent) %>%
      summarise(n = sum(n)) %>%
      left_join(activities,  by = c("antecedent" = "act"))

  writeLines(as.character(nrow(start_acts)), conn)
  if (nrow(start_acts) > 0) {
     writeLines(paste0(start_acts$id,"x",start_acts$n), conn) 
  }
  
  end_acts <- precedence_matrix %>%
      anti_join(precedence_matrix, by = c("consequent" = "antecedent")) %>%
      group_by(consequent) %>%
      summarise(n = sum(n)) %>%
      left_join(activities, by = c("consequent" = "act"))

  writeLines(as.character(nrow(end_acts)), conn)
  if (nrow(end_acts) > 0) {
    writeLines(paste0(end_acts$id,"x",end_acts$n), conn)  
  }

  edges <- precedence_matrix %>%
    anti_join(start_acts, by = c("antecedent", "antecedent", "n")) %>%
    anti_join(end_acts, by = c("consequent", "consequent", "n")) %>%
    left_join(activities,  by = c("antecedent" = "act")) %>%
    rename("from_id" = "id") %>%
    left_join(activities, by = c("consequent" = "act")) %>%
    rename("to_id" = "id")
  
  if (nrow(edges) > 0) {
    writeLines(paste0(edges$from_id,">",edges$to_id,"x",edges$n), conn) 
  }
  
  close(conn)
}