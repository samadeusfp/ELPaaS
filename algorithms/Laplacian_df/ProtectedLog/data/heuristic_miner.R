library(DiagrammeR)
library(dplyr)
library(scales)

dependency_matrix <- function(precedence_matrix) {

  precedence_matrix <- precedence_matrix %>%
    mutate(antecedent = as.character(antecedent),
           consequent = as.character(consequent))
  
  # FHM dependency measure
  precedence_matrix %>%
    left_join(precedence_matrix, 
              by = c("antecedent" = "consequent", "consequent" = "antecedent")) %>% 
    mutate_all(funs(replace(., is.na(.), 0))) %>%
    mutate(dep = if_else(antecedent != consequent, (n.x - n.y) / (n.x + n.y + 1), NA_real_)) %>% # dependencies
    mutate(dep = if_else(antecedent == consequent, (n.x / (n.x +1)), dep)) %>% # l1 loops
    na.omit()
} 

dependency_graph <- function(dependency_matrix,
                            rankdir = "LR", 
                            render = T) {
  
	if_end <- function(node, true, false) {
		ifelse(node %in% c("Start","End"), true, false)
	}
	if_start <- function(node, true, false) {
		ifelse(node %in% c("Start"), true, false)
	}
	
	activities <- union(dependency_matrix$antecedent, dependency_matrix$consequent)
  base_nodes <- data.frame(act = activities, stringsAsFactors = FALSE) %>%
    mutate(id = 1:n())
  
  nodes <- base_nodes %>%
			mutate(shape = if_end(act,"circle","rectangle"),
				   fontcolor = if_end(act, if_start(act, "chartreuse4","brown4"), "black"),
				   color = if_end(act, if_start(act, "chartreuse4","brown4"),"grey"),
				   label = act)

  create_node_df(n = nrow(nodes),
				   label = nodes$label,
				   shape = nodes$shape,
				   style = "rounded,filled",
				   fontcolor = nodes$fontcolor,
				   color = nodes$color,
				   penwidth = 1.5,
				   fixedsize = FALSE,
				   fontname = "Arial") -> nodes_df

  edges_df <- dependency_matrix %>%
    				left_join(base_nodes, by = c("antecedent" = "act")) %>%
					 	rename(from_id = id) %>%
    			  left_join(base_nodes, by = c("consequent" = "act")) %>%
					 	rename(to_id = id)

	create_edge_df(from = edges_df$from_id,
				   to = edges_df$to_id,
				   label =  round(edges_df$dep,2),
				   fontname = "Arial") -> edges_df
	
	create_graph(nodes_df, edges_df) %>%
		add_global_graph_attrs(attr = "rankdir", value = rankdir,attr_type = "graph") %>%
		add_global_graph_attrs(attr = "layout", value = "dot", attr_type = "graph") -> graph

	if(render == T) {
		graph %>% render_graph() -> graph
		graph %>% return()
	} else  {
		graph %>% return()
	}

}
