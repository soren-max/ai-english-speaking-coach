/** Strategy analysis types — answer structure evaluation. */

export interface StarComponent {
  present: boolean;
  score: number;
  text: string;
}

export interface AnswerAnalysis {
  answer_index: number;
  star: {
    situation: StarComponent;
    task: StarComponent;
    action: StarComponent;
    result: StarComponent;
  };
  technical_depth_score: number;
  logic_score: number;
  missing_parts: string[];
  recommendation: string;
}

export interface StrategyData {
  overall_strategy_score: number;
  star_completeness: number;
  technical_depth: number;
  project_logic: number;
  answer_analyses: AnswerAnalysis[];
  recommendations: string[];
}

/** Data for the logic completeness bar chart. */
export interface LogicChartItem {
  label: string;
  score: number;
  fullMark: number;
}
