// src/flow/types.ts
// Data shape for a personnel-approval workflow.
// A "flow" is a graph: nodes are approval steps, edges are "pass on approval" links.
import type { Role } from "../permissions/model";

export interface ApprovalNodeData {
  label: string;
  role: Role; // which role can act on this step
  comment?: string;
  // state is runtime; persisted with the flow once submitted
  state?: "pending" | "approved" | "rejected";
}

export type ApprovalNode = {
  id: string;
  type: "approval";
  position: { x: number; y: number };
  data: ApprovalNodeData;
};

export type ApprovalEdge = {
  id: string;
  source: string;
  target: string;
  label?: string;
};

export interface FlowDoc {
  id: string;
  title: string;
  nodes: ApprovalNode[];
  edges: ApprovalEdge[];
  ownerId: string;
  updatedAt: string; // ISO
}
