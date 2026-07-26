import type { RecommendationResponse, MaterialRecommendation } from "@/types";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Leaf, DollarSign, ShieldCheck, Zap } from "lucide-react";

export function RecommendationResults({ data }: { data: RecommendationResponse }) {
  const topResult = data.recommendations[0];
  const otherResults = data.recommendations.slice(1);

  return (
    <div className="space-y-6">
      {/* Top Recommendation Highlight */}
      <Card className="border-primary/50 shadow-lg bg-primary/5 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4">
          <Badge className="bg-primary text-primary-foreground">#1 Recommended</Badge>
        </div>
        <CardHeader>
          <CardDescription className="text-primary font-medium tracking-wider uppercase text-xs">
            Optimal Match • Score: {topResult.overall_score}%
          </CardDescription>
          <CardTitle className="text-3xl text-foreground mt-1">
            {topResult.material_name}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground mb-6 text-sm max-w-2xl leading-relaxed">
            {topResult.reason}
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard icon={<Leaf />} label="Carbon Footprint" value={`${topResult.predicted_co2_kg.toFixed(2)} kg`} />
            <MetricCard icon={<DollarSign />} label="Cost per Unit" value={`$${topResult.predicted_cost_per_kg.toFixed(2)}`} />
            <MetricCard icon={<ShieldCheck />} label="Strength" value={`${topResult.strength_score}/10`} />
            <MetricCard icon={<Zap />} label="Confidence" value={topResult.confidence} />
          </div>
        </CardContent>
      </Card>

      {/* Alternative Options */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <span className="w-1.5 h-6 bg-muted-foreground rounded-full mr-2"></span>
          Alternative Options
        </h3>
        <div className="grid gap-4 md:grid-cols-2">
          {otherResults.map((rec) => (
            <Card key={rec.rank} className="bg-card hover:bg-muted/30 transition-colors border-border/60">
              <CardContent className="p-5">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Rank #{rec.rank}</div>
                    <h4 className="font-semibold text-foreground">{rec.material_name}</h4>
                  </div>
                  <Badge variant="outline" className="font-mono">{rec.overall_score}%</Badge>
                </div>
                <div className="flex space-x-4 mt-4 text-xs text-muted-foreground">
                  <span className="flex items-center"><DollarSign className="w-3 h-3 mr-1" />{rec.predicted_cost_per_kg.toFixed(2)}</span>
                  <span className="flex items-center"><Leaf className="w-3 h-3 mr-1" />{rec.predicted_co2_kg.toFixed(2)}</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      
      {/* Footer Metrics */}
      <div className="text-xs text-muted-foreground flex justify-between px-2 pt-4 border-t">
        <span>Model: {data.model_version}</span>
        <span>Inference Latency: {data.inference_time_ms}ms</span>
      </div>
    </div>
  );
}

function MetricCard({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) {
  return (
    <div className="bg-background/50 border rounded-lg p-3 flex flex-col justify-between">
      <div className="text-muted-foreground mb-2 flex items-center">
        <span className="opacity-70 mr-2 [&>svg]:w-4 [&>svg]:h-4">{icon}</span>
        <span className="text-xs uppercase tracking-wider">{label}</span>
      </div>
      <div className="font-bold text-lg">{value}</div>
    </div>
  );
}
