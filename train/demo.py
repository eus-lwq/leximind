import random

def simulate_martingale_n_bets(
    initial_capital=1000,
    min_bet=10,
    max_bet=160,
    win_prob=0.5,
    num_bets=10000
):
    """
    模拟一次连续下注 num_bets 次的倍投策略，返回最终剩余本金
    - 本金 initial_capital
    - 最低下注 min_bet，输则下注翻倍（不超过 max_bet），赢则重置为 min_bet
    - 每次以 win_prob 的概率赢（获取当前下注额），以 1-win_prob 的概率输（扣除当前下注额）
    """
    capital = initial_capital
    bet = min_bet

    for _ in range(num_bets):
        # 如果本金不足以支付当前下注，提前结束
        if capital < bet:
            break
        # 决定本局输赢
        if random.random() <= win_prob:
            capital += bet
            bet = min_bet
        else:
            capital -= bet
            bet = min(bet * 2, max_bet)

    return capital

def run_simulations(
    n_runs=1000,
    initial_capital=1000,
    min_bet=10,
    max_bet=160,
    win_prob=0.5,
    num_bets=10000
):
    finals = []
    for _ in range(n_runs):
        finals.append(simulate_martingale_n_bets(
            initial_capital, min_bet, max_bet, win_prob, num_bets
        ))

    avg_final = sum(finals) / n_runs
    profit_count = sum(1 for c in finals if c > initial_capital)
    loss_count = n_runs - profit_count

    print(f"模拟场次：{n_runs}")
    print(f"每场下注次数：{num_bets}")
    print(f"初始本金：{initial_capital}")
    print(f"平均剩余本金：{avg_final:.2f}")
    print(f"盈利场次：{profit_count}，亏损场次：{loss_count}")
    print(f"盈利率：{profit_count/n_runs*100:.2f}%")

if __name__ == "__main__":
    run_simulations(
        n_runs=10000,
        initial_capital=1000,
        min_bet=10,
        max_bet=160,
        win_prob=0.5,
        num_bets=20
    )
