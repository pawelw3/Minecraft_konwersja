package com.maciej916.indreb.common.block.impl.charge_pad;

import com.maciej916.indreb.common.block.IndRebEntityBlock;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.tier.ChargePadTier;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.TextComponentUtil;
import com.maciej916.indreb.common.util.wrench.WrenchHelper;
import java.util.List;
import java.util.Random;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.network.chat.Component;
import net.minecraft.network.chat.MutableComponent;
import net.minecraft.network.chat.TranslatableComponent;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

public class BlockChargePad extends IndRebEntityBlock implements IStateFacing, IHasContainer, IStateActive {
   private final ChargePadTier chargePadTier;

   public BlockChargePad(ChargePadTier chargePadTier, Properties properties) {
      super(properties);
      this.chargePadTier = chargePadTier;
      WrenchHelper.registerAction(this).add(WrenchHelper.rotationAction()).add(WrenchHelper.dropAction());
   }

   public ChargePadTier getChargePadTier() {
      return this.chargePadTier;
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityChargePad(pos, state);
   }

   public ContainerChargePad getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerChargePad(windowId, level, pos, playerInventory, playerEntity);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.POWER_TIER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(this.chargePadTier.getEnergyTier().getLang().getTranslationKey())
                  .m_130940_(this.chargePadTier.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.TRANSFER.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER_TICK.getTranslationKey(),
                     new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.chargePadTier.getEnergyTier().getBasicTransfer())}
                  )
                  .m_130940_(this.chargePadTier.getEnergyTier().getColor())
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(EnumLang.CAPACITY.getTranslationKey()).m_130940_(ChatFormatting.GRAY),
               new TranslatableComponent(
                     EnumLang.POWER.getTranslationKey(), new Object[]{TextComponentUtil.getFormattedEnergyUnit((float)this.chargePadTier.getEnergyCapacity())}
                  )
                  .m_130940_(this.chargePadTier.getEnergyTier().getColor())
            }
         )
      );
   }

   @OnlyIn(Dist.CLIENT)
   public void m_7100_(BlockState stateIn, Level worldIn, BlockPos pos, Random rand) {
      if ((Boolean)stateIn.m_61143_(BlockStateHelper.activeProperty)) {
         Random random = worldIn.m_5822_();

         for (int i = 0; i < 20; i++) {
            double x = (double)pos.m_123341_() + 0.1 + random.nextDouble() * 0.9;
            double y = (double)(pos.m_123342_() + 1) + 0.3 + random.nextDouble() * 1.4;
            double z = (double)pos.m_123343_() + 0.1 + random.nextDouble() * 0.9;
            worldIn.m_7106_(ParticleTypes.f_123776_, x, y, z, 0.0, 100.0, 0.0);
         }
      }
   }
}
