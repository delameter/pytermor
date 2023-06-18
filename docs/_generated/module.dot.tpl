digraph G {
    pad = 0.25;
    concentrate = true;
    ranksep = .5;
    pack = 0;
    rankdir = BT;

    node [style="filled",fontname="ElementaCyr-Bold",margin="0.2,0.0",fontsize=12,shape=folder,width=1.0,height=.5];

    subgraph legend {
        node [fontname="Finlandica",fontsize=14];
        edge [style="invis"];

        legend_name [shape=plain,fontcolor="#000000",fillcolor="none",label="Abstraction level"];
        legend_low [shape=plain,fontcolor="#000000",fillcolor="none",label="Low"];
        legend_high [shape=plain,fontcolor="#000000",fillcolor="none",label="High"];
        icon_low [shape=folder,label="",fillcolor="#5f819d",width=.35,height=.2]
        icon_high [shape=tab,label="",fillcolor="#769440",width=.35,height=.2];

        icon_low -> legend_low [constraint=true,minlen=0];
        icon_high -> legend_high [constraint=true,minlen=0];
    }

    %s
}
