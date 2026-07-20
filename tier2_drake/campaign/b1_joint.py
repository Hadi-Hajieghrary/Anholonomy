"""B1 — TRUE centralized joint EKF (plan D7's oracle arm).

Joint state (error coordinates): [e_G (3) | s_1 (2) | ... | s_N (2)] with the
FULL (3 + 2N)^2 covariance — the cross-covariances between the load pose and
every agent's shape channel are exactly what the B1-lite attempt lacked (its
naive sigma chains lost to the decentralized record 0.41 vs 0.183 m; same
lesson as B3's lever diagnosis).

Propagate (50 Hz): xi from the all-agent radial WLS (zero latency — the
centralized grant); G <- G Exp(dt xi); s_j advances by the same-instant
identity using each agent's gyro; joint Phi couples s-error into G through the
Ad_m sensitivity. Updates: per-agent direction rows (sigma_i, 20 Hz) with joint
H touching (s_j, e_G-yaw); beacon (5 Hz) on e_G. Biases omitted (declared —
bounds the information advantage, as B1-lite).

Offline replay over log_sensors=True streams; run via d7_scorecard.py.
"""
import sys
sys.path.insert(0, "/workspaces/Anholonomy")
import numpy as np

from tier1_sheaf.core.se2 import SE2, Log, Exp, inv
from tier1_sheaf.core.shapes import Ad_m
from estimator_core.radial import solve_load_twist_wls
from tier2_drake.blind_harbor.sensors import KAPPA_DIR

SIG_V2 = 7.0e-4
SIGMA_PRIOR = np.diag([1.0e-3, 2.5e-3, 1.0e-4])
Q_G = np.diag([4.0e-2, 2.0e-2, 1.0e-3])          # declared record noise
Q_S = np.diag([2.0e-4, 2.0e-4])


def b1_joint_replay(cfg, L):
    N = cfg["N"]
    l = cfg["l"]
    ts = L["ts"]
    n = 3 + 2 * N
    G = np.eye(3)
    s = np.array([[L["starts"][j][2], 0.0] for j in range(N)])   # (sigma, sigma_i)
    theta_a = np.array([L["starts"][j][2] for j in range(N)])
    P = np.eye(n) * 1e-4
    for j in range(N):
        P[3 + 2 * j:5 + 2 * j, 3 + 2 * j:5 + 2 * j] = np.diag([4e-2, 4e-2])

    est_G, est_P, est_t = [], [], []
    for kr in range(1, len(ts)):
        k = kr - 1
        t = ts[kr]
        if k % 2 == 0:                                    # 50 Hz propagate
            yaw_G = np.arctan2(G[1, 0], G[0, 0])
            B, R, S2 = [], [], []
            zs = []
            for j in range(N):
                z = L["odom"][j][kr]
                zs.append(z)
                theta_a[j] += 0.02 * z[2]
                s[j, 0] = s[j, 1] + theta_a[j] - yaw_G     # same-instant identity
                B.append([np.cos(s[j, 0]), np.sin(s[j, 0]), 0.0])
                R.append(z[0] * np.cos(s[j, 1]) + z[1] * np.sin(s[j, 1]))
                S2.append(SIG_V2)
            prior = Ad_m(s[0, 0], s[0, 1], l) @ np.asarray(zs[0][:3])
            xi, Sx = solve_load_twist_wls(np.array(B), np.array(R), prior,
                                          SIGMA_PRIOR, np.array(S2))
            G = G @ Exp(0.02 * xi)
            Phi = np.eye(n)
            step = Exp(0.02 * xi)
            A_adj = np.array([[step[0, 0], step[1, 0], 0.0],
                              [step[0, 1], step[1, 1], 0.0], [0.0, 0.0, 1.0]])
            Phi[:3, :3] = A_adj
            # G <- s_j coupling: d xi / d sigma_j through the WLS row rotation
            for j in range(N):
                db = np.array([-np.sin(s[j, 0]), np.cos(s[j, 0]), 0.0]) * R[j]
                Phi[:3, 3 + 2 * j] += 0.02 * db / max(len(B), 1)
            Q = np.zeros((n, n))
            Q[:3, :3] = (2.0 * Sx + Q_G) * 0.02
            for j in range(N):
                Q[3 + 2 * j:5 + 2 * j, 3 + 2 * j:5 + 2 * j] = Q_S * 0.02
            P = Phi @ P @ Phi.T + Q
            P = 0.5 * (P + P.T)
        if k % 5 == 1:                                    # 20 Hz direction rows
            for j in range(N):
                zd, kap = L["dirs"][j][kr]
                if kap <= 0:
                    continue
                H = np.zeros((1, n))
                H[0, 4 + 2 * j] = 1.0                      # observes sigma_i,j
                Rm = 1.0 / KAPPA_DIR
                S1 = float(H @ P @ H.T) + Rm
                K = (P @ H.T / S1).ravel()
                innov = (zd - s[j, 1] + np.pi) % (2 * np.pi) - np.pi
                dx = K * innov
                G = G @ Exp(dx[:3])
                for m in range(N):
                    s[m] += dx[3 + 2 * m:5 + 2 * m]
                IKH = np.eye(n) - np.outer(K, H.ravel())
                P = IKH @ P @ IKH.T + np.outer(K, K) * Rm
                P = 0.5 * (P + P.T)
        if k % 20 == 2:                                   # 5 Hz beacon
            b = L["beacon"][kr]
            if b[3] > 0.5:
                Z = SE2(float(b[2]), np.asarray(b[:2], dtype=float))
                r = Log(inv(G) @ Z)
                H = np.zeros((3, n)); H[:, :3] = np.eye(3)
                Rm = np.diag([0.05 ** 2, 0.05 ** 2, np.radians(0.5) ** 2])
                S3 = H @ P @ H.T + Rm
                K = P @ H.T @ np.linalg.inv(S3)
                dx = K @ r
                G = G @ Exp(dx[:3])
                for m in range(N):
                    s[m] += dx[3 + 2 * m:5 + 2 * m]
                IKH = np.eye(n) - K @ H
                P = IKH @ P @ IKH.T + K @ Rm @ K.T
                P = 0.5 * (P + P.T)
        if kr % 10 == 0:
            est_G.append(G.copy()); est_P.append(P[:3, :3].copy()); est_t.append(t)
    return np.array(est_t), est_G, est_P
