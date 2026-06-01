using HarmonyLib;
using MegabonkTogether.Services;
using Microsoft.Extensions.DependencyInjection;

using static Assets.Scripts.Game.Combat.EnemySpecialAttacks.Implementations.EnemySpecialAttackFollowing;
using MegabonkTogether.Scripts;

namespace MegabonkTogether.Patches.SpecialAttack
{
    [HarmonyPatch(typeof(_DoAttack_d__5))]
    internal static class EnemySpecialAttackFollowingPatches
    {
        private static readonly ISynchronizationService synchronizationService = Plugin.Services.GetService<ISynchronizationService>();
        private static readonly IPlayerManagerService playerManagerService = Plugin.Services.GetService<IPlayerManagerService>();

        /// <summary>
        /// Intercept projectile to target the correct player instead of the orignal function targeting always the local player.
        /// </summary>
        [HarmonyPrefix]
        [HarmonyPatch(nameof(_DoAttack_d__5.MoveNext))]
        public static void MoveNext_Prefix(_DoAttack_d__5 __instance)
        {
            if (!synchronizationService.HasNetplaySessionStarted())
            {
                return;
            }

            var targetId = __instance.__4__this.enemy.GetOrAddNetEntity().TargetId;
            if (targetId.HasValue)
            {
                playerManagerService.AddGetNetplayerPositionRequest(targetId.Value);
            }
        }

        /// <summary>
        /// Remove queued request after attack is over.
        /// </summary>
        [HarmonyPostfix]
        [HarmonyPatch(nameof(_DoAttack_d__5.MoveNext))]
        public static void MoveNext_Postfix(_DoAttack_d__5 __instance)
        {
            if (!synchronizationService.HasNetplaySessionStarted())
            {
                return;
            }


            var targetId = __instance.__4__this.enemy.GetOrAddNetEntity().TargetId;
            if (targetId.HasValue)
            {
                playerManagerService.UnqueueNetplayerPositionRequest();
            }

        }
    }
}
