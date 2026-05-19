package com.maciej916.indreb.common.block.impl.rubber_wood;

import com.maciej916.indreb.common.block.IndRebBlock;
import com.maciej916.indreb.common.energy.interfaces.IEnergy;
import com.maciej916.indreb.common.interfaces.block.IStateAxis;
import com.maciej916.indreb.common.interfaces.block.IStateRubberLog;
import com.maciej916.indreb.common.interfaces.item.IElectricItem;
import com.maciej916.indreb.common.registries.ModItems;
import com.maciej916.indreb.common.registries.ModSounds;
import com.maciej916.indreb.common.registries.ModTags;
import com.maciej916.indreb.common.util.BlockStateHelper;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.concurrent.ThreadLocalRandom;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction.Axis;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.tags.TagKey;
import net.minecraft.world.Containers;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Rotation;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.tags.IReverseTag;

public class RubberLog extends IndRebBlock implements IStateRubberLog, IStateAxis {
   public RubberLog() {
      super(Properties.m_60944_(Material.f_76320_, MaterialColor.f_76362_).m_60913_(2.0F, 3.0F).m_60918_(SoundType.f_56736_).m_60977_());
   }

   public BlockState m_6843_(BlockState state, Rotation rot) {
      return switch (rot) {
         case COUNTERCLOCKWISE_90, CLOCKWISE_90 -> {
            switch ((Axis)state.m_61143_(BlockStateHelper.axisProperty)) {
               case X:
                  yield (BlockState)state.m_61124_(BlockStateHelper.axisProperty, Axis.Z);
               case Z:
                  yield (BlockState)state.m_61124_(BlockStateHelper.axisProperty, Axis.X);
               default:
                  yield state;
            }
         }
         default -> state;
      };
   }

   @Nullable
   public BlockState m_5573_(BlockPlaceContext pContext) {
      return (BlockState)this.m_49966_().m_61124_(BlockStateHelper.axisProperty, pContext.m_43719_().m_122434_());
   }

   public InteractionResult m_6227_(BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult trace) {
      List<ResourceLocation> itemTags = ForgeRegistries.ITEMS
         .tags()
         .getReverseTag(player.m_21120_(hand).m_41720_())
         .<Stream>map(IReverseTag::getTagKeys)
         .map(tagKeyStream -> tagKeyStream.map(TagKey::f_203868_).toList())
         .orElse(new ArrayList<>());
      return itemTags.contains(ModTags.TREETAPS_RES)
         ? this.dropRubber(player, player.m_21120_(hand), state, level, pos, trace)
         : super.m_6227_(state, level, pos, player, hand, trace);
   }

   private InteractionResult dropRubber(Player player, ItemStack itemStack, BlockState state, Level level, BlockPos pos, BlockHitResult trace) {
      if (level.m_5776_()) {
         return InteractionResult.PASS;
      } else {
         Random random = new Random();
         if (itemStack.m_41720_() instanceof IElectricItem electricItem) {
            IEnergy energy = electricItem.getEnergy(itemStack);
            if (energy.energyStored() == 0) {
               return InteractionResult.PASS;
            }

            energy.consumeEnergy(50, false);
         } else {
            itemStack.m_41622_(
               1,
               player,
               i -> level.m_6263_(
                     null,
                     player.m_20185_(),
                     player.m_20186_(),
                     player.m_20189_(),
                     SoundEvents.f_12018_,
                     SoundSource.BLOCKS,
                     0.5F,
                     0.4F / (random.nextFloat() * 0.4F + 0.8F)
                  )
            );
         }

         int dropCount = 0;
         if (this.isWet(state)) {
            dropCount = ThreadLocalRandom.current().nextInt(1, 4);
            BlockPos dropPos = pos.m_142300_(trace.m_82434_());
            Containers.m_18992_(
               level, (double)dropPos.m_123341_(), (double)dropPos.m_123342_(), (double)dropPos.m_123343_(), new ItemStack(ModItems.STICKY_RESIN, dropCount)
            );
            state = this.setWet(state, false);
            state = this.setDry(state, true);
            level.m_7731_(pos, state, 2);
         } else if (this.isDry(state)) {
            dropCount = ThreadLocalRandom.current().nextInt(0, 2);
            if (dropCount > 0) {
               BlockPos dropPos = pos.m_142300_(trace.m_82434_());
               Containers.m_18992_(
                  level, (double)dropPos.m_123341_(), (double)dropPos.m_123342_(), (double)dropPos.m_123343_(), new ItemStack(ModItems.STICKY_RESIN, dropCount)
               );
            }

            state = this.setDry(state, false);
            level.m_7731_(pos, state, 2);
         }

         if (dropCount > 0) {
            level.m_6263_(
               null,
               player.m_20185_(),
               player.m_20186_(),
               player.m_20189_(),
               ModSounds.TREETAP,
               SoundSource.NEUTRAL,
               1.0F,
               0.8F / (random.nextFloat() * 0.4F + 0.8F)
            );
            return InteractionResult.SUCCESS;
         } else {
            return InteractionResult.PASS;
         }
      }
   }

   public void m_7458_(BlockState pState, ServerLevel pLevel, BlockPos pPos, Random pRandom) {
      if (this.isDry(pState)) {
         int count = ThreadLocalRandom.current().nextInt(0, 6);
         if (count == 0) {
            BlockState var6 = this.setWet(pState, true);
            pState = this.setDry(var6, false);
            pLevel.m_7731_(pPos, pState, 2);
         }
      }

      super.m_7458_(pState, pLevel, pPos, pRandom);
   }
}
