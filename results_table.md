# Results Table

| Metric                                           | Model                              |   n | Result                     |
|:-------------------------------------------------|:-----------------------------------|----:|:---------------------------|
| Hallucination-free rate (overall)                | Base (gemma-4-E2B)                 |  57 | 28.1% (95% CI 18.1%–40.8%) |
| Hallucination-free rate (overall)                | Instruction-tuned (gemma-4-E2B-it) |  57 | 15.8% (95% CI 8.5%–27.4%)  |
| Hallucination-free rate — star tier              | Base                               |  27 | 51.9% (95% CI 34.0%–69.3%) |
| Hallucination-free rate — star tier              | IT                                 |  27 | 22.2% (95% CI 10.6%–40.8%) |
| Hallucination-free rate — role_player tier       | Base                               |  30 | 6.7% (95% CI 1.8%–21.3%)   |
| Hallucination-free rate — role_player tier       | IT                                 |  30 | 10.0% (95% CI 3.5%–25.6%)  |
| Hallucination-free rate — trap facts             | Base                               |  14 | 14.3% (95% CI 4.0%–39.9%)  |
| Hallucination-free rate — trap facts             | IT                                 |  14 | 14.3% (95% CI 4.0%–39.9%)  |
| Hallucination-free rate — string facts           | Base                               |  23 | 52.2% (95% CI 33.0%–70.8%) |
| Hallucination-free rate — string facts           | IT                                 |  23 | 17.4% (95% CI 7.0%–37.1%)  |
| Hallucination-free rate — numeric facts          | Base                               |  20 | 10.0% (95% CI 2.8%–30.1%)  |
| Hallucination-free rate — numeric facts          | IT                                 |  20 | 15.0% (95% CI 5.2%–36.0%)  |
| Sycophancy rate (validated a bad trade)          | IT only                            |   8 | 75.0% (95% CI 40.9%–92.9%) |
| Over-critical rate (pushed back on a fair trade) | IT only                            |   8 | 12.5% (95% CI 2.2%–47.1%)  |

# IT Behavior on Failed Responses

| Behavior on failed responses (IT)   |   Count | % of IT fails   |
|:------------------------------------|--------:|:----------------|
| answered                            |      37 | 77.1%           |
| abstain                             |      11 | 22.9%           |