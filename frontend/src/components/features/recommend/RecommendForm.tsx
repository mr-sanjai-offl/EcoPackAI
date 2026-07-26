'use client';

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, Controller } from "react-hook-form";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { ProductRequest } from "@/types";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
  product_weight_kg: z.coerce.number().positive("Weight must be greater than 0"),
  dimensions_cm: z.object({
    length: z.coerce.number().positive(),
    width: z.coerce.number().positive(),
    height: z.coerce.number().positive(),
  }),
  category: z.string().min(1, "Category is required"),
  fragile: z.boolean().default(false),
  food_grade_required: z.boolean().default(false),
  sustainability_priority: z.enum(["low", "medium", "high"]).default("high"),
});

interface RecommendFormProps {
  onSubmit: (data: ProductRequest) => void;
  isLoading: boolean;
}

export function RecommendForm({ onSubmit, isLoading }: RecommendFormProps) {
  const { register, control, handleSubmit, formState: { errors } } = useForm<z.infer<typeof formSchema>>({
    // @ts-expect-error - Zod coerce inference mismatch with react-hook-form types
    resolver: zodResolver(formSchema),
    defaultValues: {
      product_weight_kg: 1.5,
      dimensions_cm: { length: 20, width: 15, height: 10 },
      category: "Electronics",
      fragile: false,
      food_grade_required: false,
      sustainability_priority: "high",
    },
  });

  return (
    <Card className="shadow-sm border-border/50 bg-card">
      <CardHeader>
        <CardTitle>Specifications</CardTitle>
        <CardDescription>Enter product details to analyze.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit((data) => onSubmit(data as unknown as ProductRequest))} className="space-y-4">
          
          <div className="space-y-2">
            <Label>Category</Label>
            <Controller
              name="category"
              control={control}
              render={({ field }) => (
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Electronics">Electronics</SelectItem>
                    <SelectItem value="Food">Food & Beverage</SelectItem>
                    <SelectItem value="Clothing">Apparel & Fashion</SelectItem>
                    <SelectItem value="Cosmetics">Cosmetics</SelectItem>
                    <SelectItem value="Furniture">Furniture</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
            {errors.category && <p className="text-sm text-destructive">{errors.category.message}</p>}
          </div>

          <div className="space-y-2">
            <Label>Weight (kg)</Label>
            <Input type="number" step="0.1" {...register("product_weight_kg")} />
            {errors.product_weight_kg && <p className="text-sm text-destructive">{errors.product_weight_kg.message}</p>}
          </div>

          <div className="grid grid-cols-3 gap-2">
            <div className="space-y-2">
              <Label>L (cm)</Label>
              <Input type="number" {...register("dimensions_cm.length")} />
            </div>
            <div className="space-y-2">
              <Label>W (cm)</Label>
              <Input type="number" {...register("dimensions_cm.width")} />
            </div>
            <div className="space-y-2">
              <Label>H (cm)</Label>
              <Input type="number" {...register("dimensions_cm.height")} />
            </div>
          </div>

          <div className="space-y-2">
            <Label>Sustainability Priority</Label>
            <Controller
              name="sustainability_priority"
              control={control}
              render={({ field }) => (
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <SelectTrigger>
                    <SelectValue placeholder="Priority level" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="high">High (Max CO2 Reduction)</SelectItem>
                    <SelectItem value="medium">Medium (Balanced)</SelectItem>
                    <SelectItem value="low">Low (Cost Focused)</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
            {errors.sustainability_priority && <p className="text-sm text-destructive">{errors.sustainability_priority.message}</p>}
          </div>

          <Button type="submit" className="w-full mt-6" disabled={isLoading}>
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Running Inference...
              </>
            ) : (
              "Generate AI Recommendations"
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
