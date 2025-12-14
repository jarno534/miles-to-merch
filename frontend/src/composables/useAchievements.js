import { formatEffortTime, formatPower, getOrdinal } from "@/utils/formatters";

export function useAchievements() {
  const analyzeAchievements = (details, athleteSex) => {
    if (!details) return [];
    const efforts = details.segment_efforts || [];
    const bestEfforts = details.best_efforts || [];
    let options = [];

    const getPriority = (type) =>
      ({
        kom: 1,
        qom: 1,
        top10: 2,
        pr_1: 3,
        pr_2: 4,
        pr_3: 5,
        best_effort_top3: 4,
        best_effort: 6,
      }[type] || 99);

    efforts.forEach((effort) => {
      if (!effort.achievements || effort.achievements.length === 0) return;
      const overallAchievement = effort.achievements.find(
        (a) => a.type === "overall"
      );
      const prAchievement = effort.achievements.find((a) => a.type === "pr");
      let text = "",
        type = "",
        priority = 99;

      if (overallAchievement) {
        if (overallAchievement.rank === 1) {
          type = athleteSex === "F" ? "qom" : "kom";
          text = `${type.toUpperCase()} on '${effort.name}': ${formatEffortTime(
            effort.elapsed_time
          )} 👑`;
          priority = getPriority(type);
        } else if (overallAchievement.rank <= 10) {
          type = "top10";
          text = `${getOrdinal(overallAchievement.rank)} overall on '${
            effort.name
          }': ${formatEffortTime(effort.elapsed_time)} 🏆`;
          priority = getPriority(type);
        }
      } else if (prAchievement && prAchievement.rank <= 3) {
        const medals = ["🥇", "🥈", "🥉"];
        const medal = medals[prAchievement.rank - 1];
        type = `pr_${prAchievement.rank}`;
        if (prAchievement.rank === 1) {
          text = `Personal best on '${effort.name}': ${formatEffortTime(
            effort.elapsed_time
          )} ${medal}`;
        } else {
          text = `${getOrdinal(prAchievement.rank)} personal best on '${
            effort.name
          }': ${formatEffortTime(effort.elapsed_time)} ${medal}`;
        }
        priority = getPriority(type);
      }

      if (text) {
        options.push({ id: `segment_${effort.id}`, text, type, priority });
      }
    });

    bestEfforts.forEach((best) => {
      let text = "";
      let type = "best_effort";
      let priority = getPriority(type);
      const formattedValue = best.name.toLowerCase().includes("power")
        ? formatPower(best.average_watts)
        : formatEffortTime(best.elapsed_time);
      const rank = best.pr_rank;

      if (rank && rank >= 1 && rank <= 3) {
        const medal = ` ${["🥇", "🥈", "🥉"][rank - 1]}`;
        type = "best_effort_top3";
        priority = getPriority(`pr_${rank}`);
        if (rank === 1) {
          text = `Personal best ${best.name}: ${formattedValue}${medal}`;
        } else {
          text = `${getOrdinal(rank)} best ${
            best.name
          }: ${formattedValue}${medal}`;
        }
      } else {
        text = `Fastest ${best.name}: ${formattedValue}`;
      }
      options.push({
        id: `best_${best.id || best.name}`,
        text,
        type,
        priority,
      });
    });

    return options
      .sort((a, b) => a.priority - b.priority)
      .map((opt, index) => ({ ...opt, selected: true, order: index }));
  };

  return {
    analyzeAchievements,
  };
}
