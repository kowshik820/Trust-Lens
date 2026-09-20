// Canonical TrustLens safety policy.
// The Lambda evaluator mirrors these decisions for a dependency-light runtime.

permit (
    principal,
    action == Action::"allow_with_notice",
    resource
) when { context.risk_score < 31 };

permit (
    principal,
    action == Action::"require_confirmation",
    resource
) when { context.risk_score >= 31 && context.risk_score < 71 };

forbid (
    principal,
    action == Action::"interact",
    resource
) when { context.risk_score >= 71 };
