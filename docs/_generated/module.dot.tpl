# placeholders:
#   %s (nodes and edges)
#   $EDGE_COLOR
#   $LABEL_COLOR

digraph G {
    pad = 0.25;
    concentrate = true;
    ranksep = .5;
    pack = 1;
    rankdir = BT;

    node [style="filled",fontname="ProFont for Powerline",margin="0.2,0.0",fontsize=12,shape=folder,width=1.0,height=.5];
    edge [color="$EDGE_COLOR"];

    subgraph legend {
        node [fontsize=14,fontcolor="$LABEL_COLOR"];
        edge [style="invis"];

        legend_title [shape=plain,fillcolor="none",label="Abstraction level"];

        legend_low [shape=plain,fillcolor="none",label="Low"];
        legend_high [shape=plain,fillcolor="none",label="High"];
        legend_core [label="High\n(core)",shape=plain,fillcolor=none];
        icon_low [shape=folder,label="",fillcolor="#5f819d",width=.35,height=.2]
        icon_high [shape=tab,label="",fillcolor="#769440",width=.35,height=.2];
        icon_core [shape=tab,label="☢️",fillcolor="#a62400",width=.35,height=.2,fixedsize=1,fontsize=8];

        legend_low -> legend_title [constraint=1,minlen=1,headport=e];
        legend_high -> legend_low  [constraint=1,minlen=1];
        legend_core -> legend_high [constraint=1,minlen=1];
        icon_low -> legend_low [constraint=true,minlen=0];
        icon_high -> legend_high [constraint=true,minlen=0];
        icon_core -> legend_core [constraint=true,minlen=0];

    }

    %s
}
