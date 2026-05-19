package com.maciej916.indreb.common.block.impl.transformer;

import com.maciej916.indreb.common.block.IndRebEntityBlock;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnumLang;
import com.maciej916.indreb.common.interfaces.block.IElectricMachine;
import com.maciej916.indreb.common.interfaces.block.IHasContainer;
import com.maciej916.indreb.common.interfaces.block.IStateFacing;
import com.maciej916.indreb.common.tier.TransformerTier;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.TextComponentUtil;
import com.maciej916.indreb.common.util.wrench.WrenchHelper;
import java.util.List;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
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
import net.minecraft.world.level.block.state.properties.DirectionProperty;

public class BlockTransformer extends IndRebEntityBlock implements IStateFacing, IHasContainer, IElectricMachine {
   private final TransformerTier transformerTier;

   public BlockTransformer(TransformerTier transformerTier, Properties properties) {
      super(properties);
      this.transformerTier = transformerTier;
      WrenchHelper.registerAction(this).add(WrenchHelper.rotationHitAction()).add(WrenchHelper.dropAction());
   }

   public TransformerTier getTransformerTier() {
      return this.transformerTier;
   }

   @Nonnull
   public DirectionProperty getFacingProperty() {
      return BlockStateHelper.facingProperty;
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityTransformer(pos, state);
   }

   public ContainerTransformer getContainer(int windowId, Level level, BlockPos pos, Inventory playerInventory, Player playerEntity) {
      return new ContainerTransformer(windowId, level, pos, playerInventory, playerEntity);
   }

   public void m_5871_(ItemStack pStack, @Nullable BlockGetter pLevel, List<Component> pTooltip, TooltipFlag pFlag) {
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(
                     EnumLang.LOW.getTranslationKey(),
                     new Object[]{
                        new TranslatableComponent(this.transformerTier.getMinTier().getLang().getTranslationKey())
                           .m_130940_(this.transformerTier.getMinTier().getColor())
                     }
                  )
                  .m_130940_(ChatFormatting.GRAY)
            }
         )
      );
      pTooltip.add(
         TextComponentUtil.build(
            new MutableComponent[]{
               new TranslatableComponent(
                     EnumLang.HIGH.getTranslationKey(),
                     new Object[]{
                        new TranslatableComponent(this.transformerTier.getMaxTier().getLang().getTranslationKey())
                           .m_130940_(this.transformerTier.getMaxTier().getColor())
                     }
                  )
                  .m_130940_(ChatFormatting.GRAY)
            }
         )
      );
   }

   public EnergyTier getEnergyTier() {
      return this.transformerTier.getMaxTier();
   }
}
